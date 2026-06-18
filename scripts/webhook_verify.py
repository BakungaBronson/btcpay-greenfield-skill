"""
webhook_verify.py — the security core of receiving BTCPay webhooks.

Two functions, kept separate from any web framework so they are easy to unit
test and reuse:

  verify_signature(raw_body, sig_header, secret) -> bool
  is_invoice_really_settled(client, store_id, invoice_id) -> (bool, invoice)

WHY BOTH STEPS MATTER
---------------------
A webhook is just an HTTP POST to your URL. Anyone who learns your URL can POST
to it. Two independent checks stop that from costing you money:

1. SIGNATURE CHECK proves the request came from YOUR BTCPay instance: BTCPay
   signs the exact raw bytes of the body with your webhook secret (HMAC-SHA256)
   and puts `sha256=<hex>` in the `BTCPAY-SIG` header. We recompute it and
   compare with a constant-time comparison (so attackers can't time their way
   to a valid signature).

2. RE-FETCH CHECK proves the EVENT IS TRUE RIGHT NOW. Even a correctly signed
   `InvoiceSettled` body is a snapshot from the moment it was sent; it can be
   replayed or stale. Before releasing goods or sending a payout, fetch the
   invoice fresh from the API and confirm its real `status` is "Settled". Never
   act on the body's status field alone. This is the BTCPay-documented rule:
   "When processing an incoming webhook, always load the data fresh using the
   API as the data may be stale or changed in the meantime."
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Tuple

# A paid, final invoice has this status. Anything else is NOT safe to fulfil.
SETTLED = "Settled"


def verify_signature(raw_body: bytes, sig_header: str, secret: str) -> bool:
    """Return True only if `sig_header` is a valid HMAC-SHA256 of `raw_body`.

    raw_body MUST be the exact bytes received, before any JSON parse/re-encode.
    Re-serialising the JSON changes whitespace/key order and breaks the hash.
    """
    if not sig_header or not secret:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    # Constant-time compare to avoid leaking how many leading chars matched.
    return hmac.compare_digest(expected, sig_header)


def is_invoice_really_settled(
    client: Any, invoice_id: str, store_id: str | None = None
) -> Tuple[bool, dict]:
    """Fetch the invoice fresh and decide if it is safe to fulfil.

    Returns (safe_to_fulfil, invoice_dict). `safe_to_fulfil` is True only when
    the live status is "Settled". The caller can additionally inspect the
    returned invoice for `additionalStatus` == "PaidOver" (overpaid) etc.
    """
    invoice = client.get_invoice(invoice_id, store_id=store_id)
    status = invoice.get("status")
    return (status == SETTLED, invoice)
