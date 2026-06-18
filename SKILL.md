---
name: btcpay-greenfield
description: >-
  Write Python that talks to the BTCPay Server Greenfield API — creating
  invoices, registering and safely handling webhooks, issuing refunds, managing
  stores/payouts/payment requests, and spinning up a local webhook receiver.
  Use this skill whenever the user wants to integrate Bitcoin payments via BTCPay
  Server, mentions the Greenfield API, BTCPay invoices/webhooks, a "BTCPAY-SIG"
  signature, accepting BTC/Lightning payments in their own app, or asks for a
  payment server that receives BTCPay callbacks — even if they don't name the
  API explicitly. Especially use it when correctness around payment settlement
  and webhook verification matters, since getting those wrong loses money.
---

# BTCPay Server Greenfield API (Python)

Help beginners integrate the BTCPay Server Greenfield API in Python **correctly
and safely**, with the security-sensitive parts (webhook verification, payment
settlement) handled properly by default rather than left as an exercise.

BTCPay is a self-hosted Bitcoin payment processor. Greenfield is its REST API:
predictable `/api/v1/...` URLs, JSON in/out, `Authorization: token <API_KEY>`
auth. There are ~195 endpoints; most integrations touch a handful.

## What ships in this skill (read these as needed)

This is a folder, not just this file. Pull in deeper material on demand:

- `scripts/btcpay_client.py` — a small `requests`-based client. Named helpers for
  the eCommerce core, plus `.request()` as an escape hatch for any endpoint.
- `scripts/webhook_verify.py` — signature verification + "is it really settled"
  re-fetch. The security core, framework-free and unit-testable.
- `scripts/webhook_server.py` — a minimal Flask receiver that does
  verify → re-fetch → idempotency → fulfil. Spins up with one command.
- `scripts/tunnel.py` — cross-platform (Win/macOS/Linux) helper to expose the
  local receiver on a public HTTPS URL. Auto-installs ngrok if it's missing.
- `scripts/quickstart.py` — proves credentials work end to end in ~10 seconds.
- `examples/minimal_checkout.py` — the whole create→pay→fulfil loop in one file,
  including a polling alternative for scripts with no public URL.
- `references/endpoints.md` — the full endpoint list (all 195), grouped, with the
  permission each one needs. **Read this before guessing a path or field.**
- `references/permissions.md` — every permission scope + ready-made minimal-scope
  recipes (eCommerce key, read-only key, payouts key).
- `references/webhooks-and-security.md` — the deep dive: signature algorithm,
  status values, event types, idempotency, response codes, hardening checklist.

Prefer reusing and adapting these scripts over writing equivalents from scratch.
They already encode the gotchas below. When the user's need is genuinely
different, adapt them rather than starting blank.

## The one rule that prevents losing money

**Never act on a payment notification you haven't independently confirmed.**
A webhook is just an HTTP POST anyone can attempt. Two checks, both required,
before you ship a product or send a payout:

1. **Verify the `BTCPAY-SIG` signature** over the *raw* request body
   (HMAC-SHA256, constant-time compare). Proves it came from your instance.
2. **Re-fetch the invoice and confirm `status == "Settled"`.** Proves the event
   is true *now*, not a replayed or stale snapshot. This is the user's own
   example — "first verify that the invoice has indeed been settled instead of
   making the payment directly" — and it is exactly what BTCPay's docs require.

`webhook_server.py` already does both. If you write a receiver in another
framework, port both checks; do not drop either.

## Setup (do this before writing integration code)

The scripts read credentials from the environment so secrets never live in
source. Before running anything, make sure these are set (the user supplies
them — ask if you don't have them, ideally as structured questions):

- `BTCPAY_HOST` — instance URL, e.g. `https://your.btcpay.tld` (no trailing slash)
- `BTCPAY_API_KEY` — created in the UI under Account → Manage account → API keys,
  scoped to the **minimum** permissions and a **single store**
  (see `references/permissions.md`)
- `BTCPAY_STORE_ID` — the store to act on
- `BTCPAY_WEBHOOK_SECRET` — only for receiving webhooks; it's returned when you
  create the webhook

`assets/.env.example` is the template. If the user has no instance yet, they can
test against the public demo at `https://mainnet.demo.btcpayserver.org` (mainnet
demo — fine for wiring things up, don't rely on its uptime).

Recommended first step for any new setup: run `scripts/quickstart.py`. It does a
health check, validates the key, lists stores, and creates a $1 test invoice, so
you confirm the plumbing before building on it. (Its identity step calls
`/users/me`, which needs `btcpay.user.canviewprofile`; an eCommerce-only key
won't have that, so the step is skipped automatically — not an error.)

Dependencies are intentionally tiny: `requests` for the client, `flask` for the
receiver (`scripts/requirements.txt`).

## Typical workflows

**"Create invoices from my app."** Use `BTCPayClient.create_invoice(...)`. Set
the price server-side from your own catalogue — never from a value the browser
sent (see `examples/minimal_checkout.py`). Hand the customer the returned
`checkoutLink`.

**"Tell me when I've been paid."** Two options:
- *Webhook* (best for a real service): register with `create_webhook(...)`, store
  the returned secret, run `webhook_server.py` behind HTTPS. To get a public URL
  while developing, run `python scripts/tunnel.py 8080` — it installs ngrok if
  needed (cross-platform), starts the tunnel, and prints the URL to register.
  (A no-signup alternative is `cloudflared tunnel --url http://localhost:8080`
  if you already have cloudflared.) Don't trust a payment until both checks pass.
- *Polling* (fine for scripts/CLIs with no public URL): loop on `get_invoice`
  until `status == "Settled"` (see `wait_until_settled`).

**"Refund an invoice."** `client.refund_invoice(invoice_id, ...)`. Returns a link
the customer claims. Needs the refund permission (see permissions recipe).

**"Something else / an endpoint with no helper."** Look it up in
`references/endpoints.md` and call `client.request(method, path, body)` directly.
Every helper is just a wrapper over that.

## Gotchas

These are the failure points that actually bite people. The shipped scripts
already avoid them; preserve these properties when you adapt them.

- **Hashing the wrong bytes.** Webhook signatures are computed over the *raw*
  body. The instant you parse JSON and re-serialise it, whitespace/key order
  change and the signature will never match. Capture raw bytes
  (`request.get_data()` in Flask) and hash those.
- **Trusting the webhook's `status` field.** The body can be replayed or stale.
  Re-fetch the invoice and read the live `status`. The fresh `GET` is the source
  of truth, always.
- **Fulfilling on `Processing`.** Only `Settled` is final. `Processing` means
  paid-but-not-yet-confirmed; treat it as not-yet-paid unless you have
  deliberately accepted 0-conf risk for low-value items.
- **Non-idempotent handlers.** Deliveries repeat (retries, manual redelivery,
  multiple events). Key on `invoiceId`/`orderId` and record fulfilment so you
  never ship or pay twice. Prefer a unique DB constraint over an in-memory set
  in production.
- **Wrong response code.** Return `2xx` only once you've durably handled the
  event; return non-2xx on *transient* failure so BTCPay redelivers. But return
  `400` for a bad signature (it won't get better on retry).
- **Amounts as floats.** Send `amount` as a string (`"10.00"`). The API treats
  monetary values as decimal strings to avoid float rounding; the client does
  this for you.
- **Over-broad API keys.** A key created with no permissions is *unrestricted*.
  Always pass an explicit, minimal scope list, bound to one store with the
  `permission:STORE_ID` form.
- **Basic Auth for everything.** Prefer API keys. Basic Auth is only for the few
  bootstrap endpoints (create a user / create a store on behalf of a user).
- **`paymentMethod` naming.** Recent BTCPay uses ids like `BTC-CHAIN`, `BTC-LN`,
  `BTC-LNURL`, `ARKADE`. Don't assume `BTC-CHAIN` exists — a store with on-chain
  disabled (e.g. Lightning-only) has none, so the refund/payout default will 400.
  Confirm the live values first with `client.get_payment_methods()` (wraps
  `GET /api/v1/stores/{storeId}/payment-methods`) rather than guessing.
- **`payoutMethodId` vs `paymentMethod` on refunds/payouts.** Current BTCPay
  renamed the refund/payout body field `paymentMethod` → `payoutMethodId`. The
  old name is *silently ignored* (no 400), producing a refund with NO usable
  payout method — the customer's claim page then rejects every address ("A valid
  address was not provided"). The client sends `payoutMethodId` (and keeps
  `paymentMethod` for old instances). Verified live against the demo.
- **Refunds need a payout route.** A refund creates a pull payment the customer
  claims. To actually *pay* a claimed Lightning refund the store needs a payout
  source (a Lightning automated payout processor, or the owner approves+sends
  manually). With no processor, claims sit in Payouts awaiting approval.
- **Overpayment.** Check `additionalStatus == "PaidOver"` (or the settled
  event's `overPaid`) if you need to handle refunding the difference.

## Verifying your work

For anything involving invoices or webhooks, sanity-check against a real (demo)
instance when possible: create an invoice, fetch it back, confirm the fields you
depend on actually exist in the response. For webhook code, unit-test
`verify_signature` with a known secret/body/signature triple before trusting it —
a verifier that always returns True is worse than none.

## Keep improving this skill

Most good skills start small and grow. When a real BTCPay integration surfaces a
new gotcha (an endpoint that behaves unexpectedly, a field that moved, a
framework-specific raw-body trick), add it to the Gotchas section or the
security reference so the next run benefits.
