"""
webhook_server.py — a minimal, spin-up-in-seconds BTCPay webhook receiver.

  pip install flask requests
  export BTCPAY_HOST=... BTCPAY_API_KEY=... BTCPAY_STORE_ID=... BTCPAY_WEBHOOK_SECRET=...
  python webhook_server.py
  # then expose it publicly (cross-platform, auto-installs ngrok if missing):
  #   python tunnel.py 8080
  # and register the printed URL with client.create_webhook(url=URL+"/btcpay-webhook", ...)

What this does on every POST to /btcpay-webhook, in order:
  1. Read the RAW body (needed for the signature).
  2. Verify the BTCPAY-SIG HMAC. Reject with 400 if it doesn't match.
  3. Skip if we've already processed this deliveryId/invoice (idempotency).
  4. On a settlement event, RE-FETCH the invoice and confirm status==Settled
     before running your fulfilment code. Never trust the body's status.
  5. Return 200 only once handled. Returning non-2xx makes BTCPay redeliver.

The fulfilment step (`fulfil_order`) is a stub — replace it with your own
logic (mark the order paid, send the product, trigger a payout, etc.).
"""

from __future__ import annotations

import logging
import os
import threading

from flask import Flask, request

from btcpay_client import BTCPayClient
from webhook_verify import verify_signature, is_invoice_really_settled

# Use logging, NOT print(): print() is block-buffered when stdout isn't a TTY
# (systemd, Docker, a redirected log file), so "I fulfilled order X" can appear
# late or be lost entirely on shutdown — unacceptable for a payment processor.
# logging flushes each record and carries timestamps/levels.
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("btcpay-webhook")

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("BTCPAY_WEBHOOK_SECRET", "")
STORE_ID = os.environ.get("BTCPAY_STORE_ID")

client = BTCPayClient.from_env()

# Events that mean "money is final". We re-fetch and fulfil on these.
SETTLEMENT_EVENTS = {"InvoiceSettled", "InvoicePaymentSettled"}

# --- tiny in-memory idempotency guard --------------------------------------
# Webhooks can be redelivered (network retries, manual redelivery, multiple
# events per invoice). Processing the same settlement twice could mean shipping
# twice or paying out twice. In production use a DB row / unique constraint
# keyed on invoice_id; this in-memory set just demonstrates the shape.
_processed_lock = threading.Lock()
_processed_invoices: set[str] = set()


def already_fulfilled(invoice_id: str) -> bool:
    with _processed_lock:
        return invoice_id in _processed_invoices


def mark_fulfilled(invoice_id: str) -> None:
    with _processed_lock:
        _processed_invoices.add(invoice_id)


def fulfil_order(invoice: dict) -> None:
    """REPLACE ME with your real logic. Runs only after both checks pass."""
    meta = invoice.get("metadata") or {}
    order_id = meta.get("orderId", "(no orderId in metadata)")
    overpaid = invoice.get("additionalStatus") == "PaidOver"
    log.info("[FULFIL] invoice=%s order=%s amount=%s %s overpaid=%s",
             invoice["id"], order_id, invoice.get("amount"),
             invoice.get("currency"), overpaid)


@app.post("/btcpay-webhook")
def btcpay_webhook():
    raw = request.get_data()  # exact bytes — do NOT use request.json here
    sig = request.headers.get("BTCPAY-SIG", "")

    # 1 + 2: authenticity
    if not verify_signature(raw, sig, WEBHOOK_SECRET):
        # 400, not 500: a bad signature is a bad request, and we don't want
        # BTCPay to keep redelivering a forged/misconfigured call forever.
        return "invalid signature", 400

    event = request.get_json(silent=True) or {}
    event_type = event.get("type")
    invoice_id = event.get("invoiceId")

    # We only act on settlement events; acknowledge the rest so they aren't
    # redelivered.
    if event_type not in SETTLEMENT_EVENTS or not invoice_id:
        log.info("[IGNORE] type=%s invoice=%s (not a settlement event)",
                 event_type, invoice_id)
        return "", 200

    # 3: idempotency
    if already_fulfilled(invoice_id):
        log.info("[DEDUP] %s already fulfilled — acknowledging without re-running",
                 invoice_id)
        return "", 200

    # 4: re-fetch and confirm the live status before doing anything costly
    safe, invoice = is_invoice_really_settled(client, invoice_id, store_id=STORE_ID)
    if not safe:
        # Signed event said settled but the live invoice isn't. Acknowledge so
        # it isn't hammered; the correct settlement event will arrive/await.
        log.info("[SKIP] %s live status=%s not Settled",
                 invoice_id, invoice.get("status"))
        return "", 200

    fulfil_order(invoice)
    mark_fulfilled(invoice_id)
    return "", 200


@app.get("/health")
def health():
    return {"ok": True}, 200


if __name__ == "__main__":
    if not WEBHOOK_SECRET:
        raise SystemExit(
            "BTCPAY_WEBHOOK_SECRET is not set. It is returned when you create a "
            "webhook (client.create_webhook). Without it, signatures cannot be "
            "verified and every delivery would be rejected."
        )
    port = int(os.environ.get("PORT", "8080"))
    # Flask's dev server is fine for local testing. For production, run behind
    # gunicorn/uvicorn + a reverse proxy with HTTPS.
    app.run(host="0.0.0.0", port=port)
