# BTCPay Greenfield — Webhooks & Security

This is the highest-stakes part of any BTCPay integration: it is where an
attacker who can POST to your URL would try to trick you into releasing goods or
money. Read it before writing a receiver.

## The two-check rule (do not skip either)

When a webhook arrives:

1. **Verify the signature.** BTCPay signs the exact raw body with your webhook
   secret using HMAC-SHA256 and sends `sha256=<hex>` in the `BTCPAY-SIG` header.
   Recompute it over the raw bytes and compare with a constant-time comparison.
   A mismatch means the request is forged or misconfigured — reject it.

2. **Re-fetch the invoice and confirm it is really `Settled`.** A signed body is
   still a point-in-time snapshot and can be replayed or arrive out of order.
   Before doing anything irreversible, `GET` the invoice and check the live
   `status`. The BTCPay docs state it plainly: always load the data fresh from
   the API because the webhook data may be stale or changed in the meantime.

`scripts/webhook_verify.py` implements both; `scripts/webhook_server.py` wires
them into a runnable server.

## Signature verification, by language

The algorithm is identical everywhere: `HMAC_SHA256(secret, raw_body)`, hex
encode, prefix with `sha256=`, constant-time compare to `BTCPAY-SIG`.

Python (what the skill ships):
```python
import hmac, hashlib
expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
ok = hmac.compare_digest(expected, sig_header)
```

The single most common bug: hashing a re-serialised body. You must hash the
**raw bytes as received**. In Flask use `request.get_data()`; in FastAPI use
`await request.body()`; in Node capture `req.rawBody` via a body-parser verify
hook. Once you call `request.json` and re-encode, whitespace and key order
change and the hash will never match.

## Invoice status values

`status` (the field you gate fulfilment on):
- `New` — created, not yet paid. Do nothing.
- `Processing` — paid but not enough confirmations / still settling. Do NOT
  fulfil yet unless you have explicitly opted into 0-conf risk.
- `Settled` — final and paid. Safe to fulfil.
- `Expired` — time ran out without sufficient payment.
- `Invalid` — failed / problematic.

`additionalStatus` adds nuance: `PaidOver` (overpaid), `PaidPartial`,
`PaidLate`, `Marked`, `None`. For overpayment you may owe the customer a refund
of the difference.

## Webhook event types

Invoice lifecycle:
- `InvoiceCreated`
- `InvoiceReceivedPayment`
- `InvoiceProcessing`
- `InvoiceExpired`
- `InvoiceSettled` ← the usual "money is final, fulfil now" trigger
- `InvoiceInvalid`
- `InvoicePaymentSettled`

Payment requests: `PaymentRequestCreated`, `PaymentRequestUpdated`,
`PaymentRequestArchived`, `PaymentRequestStatusChanged`.

Payouts: `PayoutCreated`, `PayoutApproved`, `PayoutUpdated`.

Subscriptions: `SubscriberCreated`, `SubscriberCredited`, `SubscriberCharged`,
`SubscriberActivated`, `SubscriberPhaseChanged`, `SubscriberDisabled`,
`PaymentReminder`, `PlanStarted`, `SubscriberNeedUpgrade`.

Subscribe to everything with `authorizedEvents.everything = true`, or narrow it
to `specificEvents: ["InvoiceSettled", ...]`.

## Webhook payload fields you will use

Every delivery includes: `deliveryId`, `webhookId`, `originalDeliveryId`,
`isRedelivery`, `type`, `timestamp`. Invoice events add `storeId`, `invoiceId`,
`metadata`. The `InvoiceSettled` event additionally carries `manuallyMarked` and
`overPaid` booleans.

## Idempotency (or: how not to ship twice)

Deliveries can repeat: network retries, manual redelivery from the UI, and
multiple events per invoice all happen normally. Make your handler idempotent —
key on `invoiceId` (or your own `orderId` from metadata) and record that you've
fulfilled it, ideally with a unique DB constraint so two concurrent deliveries
can't both win. `isRedelivery` and `deliveryId` help with logging/debugging but
are not a substitute for your own dedup.

## Responding correctly

- Return `2xx` once you've durably accepted the event. BTCPay marks it
  delivered.
- Return non-2xx (or time out) and BTCPay will **redeliver** later. Use this on
  transient failures (your DB was down) so you don't lose the event. Do NOT
  return non-2xx for a bad signature — that's not transient; return 400 and move
  on.
- Acknowledge events you don't care about with `200` so they aren't retried.

## Broader hardening checklist

- API keys: minimum scopes, single store, rotate periodically. Never commit
  them; load from env (`BTCPayClient.from_env()`).
- Prefer API keys over Basic Auth everywhere except the few bootstrap endpoints
  (create user / create store on behalf of a user).
- Set prices server-side. Create invoices from your backend; never let the
  browser dictate `amount`.
- Serve your webhook endpoint over HTTPS only.
- Don't store redundant customer PII on the invoice metadata — it widens the
  blast radius if either system is breached.
- Treat `Processing` as "not yet paid" for fulfilment unless you have
  deliberately accepted 0-confirmation risk for low-value items.
