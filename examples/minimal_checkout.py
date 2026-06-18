"""
minimal_checkout.py — the whole eCommerce loop in one readable file.

This shows the shape of a real integration without a web framework getting in
the way:

  1. Server-side, create an invoice for a fixed price (NEVER trust a price
     sent by the browser).
  2. Give the customer `checkoutLink`.
  3. When BTCPay calls your webhook, verify -> re-fetch -> fulfil (that part
     lives in webhook_server.py).
  4. For a script/CLI flow with no public URL, you can POLL instead of using a
     webhook — shown here as `wait_until_settled`.

Run:
  pip install requests
  export BTCPAY_HOST=... BTCPAY_API_KEY=... BTCPAY_STORE_ID=...
  python minimal_checkout.py
"""

from __future__ import annotations

import sys
import time

# Make the sibling scripts/ importable when running from examples/.
sys.path.insert(0, "../scripts")
sys.path.insert(0, "scripts")

from btcpay_client import BTCPayClient  # noqa: E402
from webhook_verify import SETTLED  # noqa: E402

# Your real catalogue lives server-side. The browser sends an item id, never a
# price — you look the price up here so a tampered request can't underpay.
CATALOGUE = {
    "tea-sampler": {"amount": "12.50", "currency": "USD"},
    "mug": {"amount": "8.00", "currency": "USD"},
}


def start_checkout(client: BTCPayClient, item_id: str, order_id: str) -> dict:
    item = CATALOGUE[item_id]  # KeyError = unknown item = reject
    invoice = client.create_invoice(
        amount=item["amount"],
        currency=item["currency"],
        metadata={"orderId": order_id, "itemId": item_id},
    )
    print(f"Invoice {invoice['id']} created. Send the customer here:")
    print(f"  {invoice['checkoutLink']}")
    return invoice


def wait_until_settled(client: BTCPayClient, invoice_id: str,
                       timeout_s: int = 120, poll_s: int = 5) -> dict:
    """Polling alternative to webhooks for scripts with no public endpoint.

    The re-fetch IS the source of truth here too — we only return success when
    the live status is Settled.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        inv = client.get_invoice(invoice_id)
        status = inv["status"]
        print(f"  status={status}")
        if status == SETTLED:
            return inv
        if status in ("Expired", "Invalid"):
            raise RuntimeError(f"Invoice {invoice_id} ended as {status}")
        time.sleep(poll_s)
    raise TimeoutError(f"Invoice {invoice_id} not settled within {timeout_s}s")


if __name__ == "__main__":
    client = BTCPayClient.from_env()
    inv = start_checkout(client, item_id="tea-sampler", order_id="DEMO-1")
    print("\nWaiting for payment (Ctrl-C to stop)...")
    try:
        settled = wait_until_settled(client, inv["id"])
        print(f"\nSettled! Safe to fulfil order {settled['metadata']['orderId']}.")
    except (TimeoutError, RuntimeError) as e:
        print(f"\nNot fulfilling: {e}")
