# BTCPay Greenfield Skill (Python)

A [Claude](https://claude.com/claude-code) **Agent Skill** for integrating the
[BTCPay Server](https://btcpayserver.org) **Greenfield API** in Python — creating
invoices, receiving and *safely* verifying webhooks, issuing refunds, and managing
stores / payouts / payment requests. It gets the security-sensitive parts
(webhook signature verification and payment settlement) right **by default**,
because getting those wrong loses money.

BTCPay is a self-hosted Bitcoin payment processor. Greenfield is its REST API:
predictable `/api/v1/...` URLs, JSON in/out, `Authorization: token <API_KEY>`.

## What's inside

| File | What it is |
|---|---|
| `SKILL.md` | The skill instructions (the entry point Claude reads). |
| `scripts/btcpay_client.py` | Small `requests`-based client. Named helpers for the eCommerce core + `.request()` escape hatch for any of the ~195 endpoints. |
| `scripts/webhook_verify.py` | The security core: HMAC-SHA256 signature verification + "is it really settled" re-fetch. Framework-free, unit-testable. |
| `scripts/webhook_server.py` | A minimal Flask receiver doing verify → re-fetch → idempotency → fulfil. |
| `scripts/tunnel.py` | Cross-platform helper to expose the local receiver on a public HTTPS URL. **Auto-installs ngrok** (Win/macOS/Linux) if it's missing. |
| `scripts/quickstart.py` | Proves your credentials work end to end in ~10 seconds. |
| `examples/minimal_checkout.py` | The whole create → pay → fulfil loop in one file (with a polling alternative). |
| `references/` | Full endpoint list, permission scopes + minimal-scope recipes, and a webhooks/security deep-dive. |
| `btcpay-greenfield.skill` | The packaged skill (a zip) for one-step install. |

## Quickstart

```bash
pip install requests flask
export BTCPAY_HOST=https://your.btcpay.tld     # or the public demo below
export BTCPAY_API_KEY=...                       # Account → Manage account → API keys
export BTCPAY_STORE_ID=...
python scripts/quickstart.py
```

No instance yet? Test against the public demo at
`https://mainnet.demo.btcpayserver.org` (it's mainnet — fine for wiring things up).

Create an API key scoped to the **minimum** permissions and a **single store**
(see `references/permissions.md` for ready-made recipes).

## The one rule that prevents losing money

**Never act on a payment notification you haven't independently confirmed.**
A webhook is just an HTTP POST anyone can attempt. Two checks, both required,
before you ship a product or send a payout:

1. **Verify the `BTCPAY-SIG` signature** over the *raw* request body (HMAC-SHA256,
   constant-time compare). Proves it came from your instance.
2. **Re-fetch the invoice and confirm `status == "Settled"`.** Proves the event
   is true *now*, not replayed or stale.

`webhook_server.py` does both.

## Receiving webhooks locally

```bash
python scripts/webhook_server.py                 # terminal 1
python scripts/tunnel.py 8080                     # terminal 2 — prints a public HTTPS URL
# register the printed URL: client.create_webhook(url=URL + "/btcpay-webhook", ...)
```

## Install as a Claude skill

Drop the `btcpay-greenfield/` folder (or unzip `btcpay-greenfield.skill`) into your
Claude skills directory, or upload the `.skill` file in Claude. See the
[Agent Skills docs](https://docs.claude.com/en/docs/claude-code/skills).

## Notes

- This skill was built and then **tested live against the BTCPay demo** — including
  a real Lightning payment, webhook delivery + verification, idempotent fulfilment,
  and a Lightning refund. Several real-world gotchas (e.g. the refund/payout
  `paymentMethod` → `payoutMethodId` field rename) are baked into the code and the
  Gotchas section of `SKILL.md`.
- Keep secrets in the environment, never in source. `assets/.env.example` is the
  template; copy it to `.env` (which is gitignored).

## License

[MIT](LICENSE).
