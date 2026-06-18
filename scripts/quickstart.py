"""
quickstart.py — prove your credentials work end to end in ~10 seconds.

  pip install requests
  export BTCPAY_HOST=https://your.btcpay.tld
  export BTCPAY_API_KEY=...
  export BTCPAY_STORE_ID=...        # optional; the script can list stores for you
  python quickstart.py

It runs read-only checks first, then (only if a store is known) creates a tiny
test invoice so you can see the full create -> fetch round trip. Nothing here
moves real money: an unpaid invoice just expires.
"""

from __future__ import annotations

import sys

from btcpay_client import BTCPayClient, BTCPayError


def main() -> int:
    try:
        client = BTCPayClient.from_env()
    except RuntimeError as e:
        print(f"Setup error: {e}")
        return 1

    print(f"Host: {client.host}")

    try:
        print("1) Health check...")
        client.health()
        print("   OK — instance reachable.")

        print("2) Who am I (validates the API key)...")
        try:
            me = client.whoami()
            print(f"   OK — authenticated as {me.get('email', me.get('id'))}")
        except BTCPayError as e:
            # /users/me needs btcpay.user.canviewprofile, which an eCommerce-only
            # key legitimately may not have. Don't fail the whole check over an
            # optional identity lookup — step 3 still proves the key works against
            # the store.
            if e.status_code in (401, 403):
                print("   (skipped — key lacks btcpay.user.canviewprofile; "
                      "harmless for eCommerce. Validating via store access instead.)")
            else:
                raise

        print("3) Listing stores this key can see...")
        stores = client.get_stores()
        for s in stores:
            print(f"   - {s.get('name')}  (id={s.get('id')})")
        if not client.store_id and stores:
            client.store_id = stores[0]["id"]
            print(f"   Using first store: {client.store_id}")

        if not client.store_id:
            print("No store available; set BTCPAY_STORE_ID to test invoice creation.")
            return 0

        print("4) Creating a $1.00 test invoice...")
        inv = client.create_invoice(
            amount="1.00", currency="USD",
            metadata={"orderId": "quickstart-test"},
        )
        print(f"   Created invoice {inv['id']} — status={inv['status']}")
        print(f"   Checkout link: {inv.get('checkoutLink')}")

        print("5) Re-fetching that invoice (your source of truth)...")
        fresh = client.get_invoice(inv["id"])
        print(f"   Live status: {fresh['status']}")

        print("\nAll checks passed. You're ready to build.")
        return 0

    except BTCPayError as e:
        print(f"\nAPI error: HTTP {e.status_code}")
        print(f"  {e.method} {e.url}")
        print(f"  body: {e.body}")
        if e.status_code in (401, 403):
            print("  -> Check the API key is valid and has the right permissions "
                  "for this store (see references/permissions.md).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
