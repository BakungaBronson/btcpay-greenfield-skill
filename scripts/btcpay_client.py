"""
btcpay_client.py — a small, dependency-light client for the BTCPay Server
Greenfield API.

Design goals (for beginners):
  - One class, plain `requests`, no code generation, no magic.
  - Every method maps to one documented endpoint so you can cross-reference
    it against references/endpoints.md.
  - Helpful errors: a failed call raises BTCPayError with the HTTP status and
    the server's error body, instead of a bare stack trace.

It deliberately covers the eCommerce core (stores, invoices, webhooks, refunds,
payouts, payment requests). For the full 195-endpoint surface, use `request()`
directly — every helper below is just a thin wrapper over it.

Usage:
    from btcpay_client import BTCPayClient
    client = BTCPayClient("https://your.btcpay.tld", api_key="...", store_id="...")
    inv = client.create_invoice(amount="10.00", currency="USD",
                                metadata={"orderId": "SN-1042"})
    print(inv["id"], inv["checkoutLink"])
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import requests


class BTCPayError(RuntimeError):
    """Raised when the API returns a non-2xx response.

    BTCPay returns a JSON body like {"code": "...", "message": "..."} or a list
    of such objects for validation errors. We surface that verbatim so you know
    exactly what went wrong.
    """

    def __init__(self, status_code: int, body: Any, method: str, url: str):
        self.status_code = status_code
        self.body = body
        self.method = method
        self.url = url
        super().__init__(f"{method} {url} -> HTTP {status_code}: {body}")


class BTCPayClient:
    def __init__(
        self,
        host: str,
        api_key: str,
        store_id: Optional[str] = None,
        timeout: int = 30,
    ):
        if not host:
            raise ValueError("host is required, e.g. https://your.btcpay.tld")
        if not api_key:
            raise ValueError("api_key is required")
        # Normalise: strip trailing slash so path joins are predictable.
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.store_id = store_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {api_key}",
                "Content-Type": "application/json",
            }
        )

    # ---- factory ---------------------------------------------------------

    @classmethod
    def from_env(cls) -> "BTCPayClient":
        """Build a client from BTCPAY_HOST / BTCPAY_API_KEY / BTCPAY_STORE_ID.

        Keeping secrets in the environment (not in code) is the single easiest
        security win. See assets/.env.example.
        """
        host = os.environ.get("BTCPAY_HOST")
        key = os.environ.get("BTCPAY_API_KEY")
        store = os.environ.get("BTCPAY_STORE_ID")
        missing = [n for n, v in [("BTCPAY_HOST", host), ("BTCPAY_API_KEY", key)] if not v]
        if missing:
            raise RuntimeError(
                f"Missing env vars: {', '.join(missing)}. "
                f"Copy assets/.env.example to .env and fill it in."
            )
        return cls(host, key, store)

    # ---- core ------------------------------------------------------------

    def request(self, method: str, path: str, body: Optional[dict] = None,
                params: Optional[dict] = None) -> Any:
        """Make a raw call. `path` starts with /api/v1/...

        This is the escape hatch: any endpoint in references/endpoints.md that
        doesn't have a named helper can be called with this directly.
        """
        url = f"{self.host}{path}"
        resp = self.session.request(
            method.upper(),
            url,
            data=json.dumps(body) if body is not None else None,
            params=params,
            timeout=self.timeout,
        )
        if not resp.ok:
            try:
                err_body = resp.json()
            except ValueError:
                err_body = resp.text
            raise BTCPayError(resp.status_code, err_body, method.upper(), url)
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    def _store(self, store_id: Optional[str]) -> str:
        sid = store_id or self.store_id
        if not sid:
            raise ValueError(
                "store_id not set. Pass it to the method or to the constructor."
            )
        return sid

    # ---- connectivity ----------------------------------------------------

    def health(self) -> Any:
        """GET /api/v1/health — no auth needed; good for a connectivity check."""
        return self.request("GET", "/api/v1/health")

    def whoami(self) -> Any:
        """GET /api/v1/users/me — confirms your API key is valid."""
        return self.request("GET", "/api/v1/users/me")

    def get_stores(self) -> Any:
        return self.request("GET", "/api/v1/stores")

    def get_store(self, store_id: Optional[str] = None) -> Any:
        return self.request("GET", f"/api/v1/stores/{self._store(store_id)}")

    def get_payment_methods(self, store_id: Optional[str] = None) -> Any:
        """GET .../payment-methods — the store's payment methods.

        Use this to discover the live `paymentMethodId` values before a refund or
        payout instead of guessing. Naming varies by instance/config: a store may
        expose "BTC-CHAIN", "BTC-LN", "BTC-LNURL", "ARKADE", etc. — and a store
        with on-chain disabled has NO "BTC-CHAIN" at all. Each item looks like
        {"enabled": true, "paymentMethodId": "BTC-LN"}.
        """
        return self.request(
            "GET", f"/api/v1/stores/{self._store(store_id)}/payment-methods"
        )

    def enabled_payment_methods(self, store_id: Optional[str] = None) -> list[str]:
        """Just the enabled `paymentMethodId` strings, e.g. ["BTC-LN", "ARKADE"]."""
        return [
            m["paymentMethodId"]
            for m in self.get_payment_methods(store_id)
            if m.get("enabled")
        ]

    # Auto-selection order for refunds/payouts: Lightning first (instant, cheap,
    # and the most broadly enabled on modern stores), then LNURL, then on-chain.
    PAYMENT_METHOD_PREFERENCE = ("BTC-LN", "BTC-LNURL", "BTC-CHAIN")

    def resolve_payment_method(
        self, preferred: Optional[str] = None, store_id: Optional[str] = None
    ) -> str:
        """Return a payment method the store actually has ENABLED.

        - `preferred` given: returned only if it's enabled, else ValueError that
          lists what IS enabled (so a wrong guess fails loudly, not silently).
        - `preferred` None: picks the first enabled method in
          PAYMENT_METHOD_PREFERENCE order — i.e. Lightning by default — falling
          back to the first enabled method of any kind.

        Costs one GET .../payment-methods. Worth it before moving money: it turns
        the "BTC-CHAIN doesn't exist here" 400 into a clear, upfront error.
        """
        enabled = self.enabled_payment_methods(store_id)
        if not enabled:
            raise ValueError("This store has no enabled payment methods.")
        if preferred:
            if preferred in enabled:
                return preferred
            raise ValueError(
                f"Payment method {preferred!r} is not enabled on this store. "
                f"Enabled methods: {enabled}"
            )
        for pm in self.PAYMENT_METHOD_PREFERENCE:
            if pm in enabled:
                return pm
        return enabled[0]

    # ---- invoices --------------------------------------------------------

    def create_invoice(
        self,
        amount: Optional[str] = None,
        currency: str = "USD",
        metadata: Optional[dict] = None,
        checkout: Optional[dict] = None,
        store_id: Optional[str] = None,
    ) -> Any:
        """POST /api/v1/stores/{storeId}/invoices

        `amount` is a STRING to avoid float rounding (e.g. "10.00"). If amount
        is None the invoice is a top-up invoice (accepts any payment as full).
        `metadata` can hold your own orderId, buyerEmail, etc. — but don't put
        sensitive customer data here.
        """
        body: dict[str, Any] = {"currency": currency}
        if amount is not None:
            body["amount"] = str(amount)
        if metadata:
            body["metadata"] = metadata
        if checkout:
            body["checkout"] = checkout
        return self.request(
            "POST", f"/api/v1/stores/{self._store(store_id)}/invoices", body
        )

    def get_invoice(self, invoice_id: str, store_id: Optional[str] = None) -> Any:
        """GET a single invoice. THIS is your source of truth for status."""
        return self.request(
            "GET",
            f"/api/v1/stores/{self._store(store_id)}/invoices/{invoice_id}",
        )

    def list_invoices(self, store_id: Optional[str] = None, **params: Any) -> Any:
        return self.request(
            "GET",
            f"/api/v1/stores/{self._store(store_id)}/invoices",
            params=params or None,
        )

    def refund_invoice(
        self,
        invoice_id: str,
        refund_variant: str = "CurrentRate",
        payment_method: Optional[str] = None,
        store_id: Optional[str] = None,
        **extra: Any,
    ) -> Any:
        """POST .../invoices/{id}/refund — returns a link the customer claims.

        refund_variant is one of: CurrentRate, RateThen, Fiat, OverpaidAmount,
        Custom. `payment_method=None` (default) auto-selects an ENABLED method,
        Lightning first (see resolve_payment_method) — so this works on
        Lightning-only stores instead of assuming on-chain. Pass an explicit id
        to override; if it isn't enabled you get a clear error, not a raw 400.

        The method id goes in `payoutMethodId` (this is what selects how the
        refund pays out — e.g. Lightning). Current BTCPay renamed the old
        `paymentMethod` field to `payoutMethodId`; sending the old name is
        SILENTLY IGNORED, producing a refund with no usable payout method (the
        claim page then rejects every address). We send `payoutMethodId` and keep
        `paymentMethod` too, so this works on both new and old instances.
        """
        pm = self.resolve_payment_method(payment_method, store_id=store_id)
        body = {"refundVariant": refund_variant,
                "payoutMethodId": pm, "paymentMethod": pm}
        body.update(extra)
        return self.request(
            "POST",
            f"/api/v1/stores/{self._store(store_id)}/invoices/{invoice_id}/refund",
            body,
        )

    # ---- webhooks --------------------------------------------------------

    def create_webhook(
        self,
        url: str,
        secret: Optional[str] = None,
        events: Optional[list[str]] = None,
        store_id: Optional[str] = None,
    ) -> Any:
        """POST .../webhooks. The RESPONSE contains the `secret` you must store
        to verify future deliveries. If you don't pass one, BTCPay generates it.
        `events=None` subscribes to everything; otherwise pass specific types
        like ["InvoiceSettled", "InvoicePaymentSettled"].
        """
        body: dict[str, Any] = {"url": url, "enabled": True}
        if secret is not None:
            body["secret"] = secret
        if events is None:
            body["authorizedEvents"] = {"everything": True}
        else:
            body["authorizedEvents"] = {"everything": False, "specificEvents": events}
        return self.request(
            "POST", f"/api/v1/stores/{self._store(store_id)}/webhooks", body
        )

    def list_webhooks(self, store_id: Optional[str] = None) -> Any:
        return self.request(
            "GET", f"/api/v1/stores/{self._store(store_id)}/webhooks"
        )

    def delete_webhook(self, webhook_id: str, store_id: Optional[str] = None) -> Any:
        return self.request(
            "DELETE",
            f"/api/v1/stores/{self._store(store_id)}/webhooks/{webhook_id}",
        )

    # ---- payment requests & payouts (common eCommerce extras) ------------

    def create_payment_request(self, amount: str, currency: str = "USD",
                               title: str = "", store_id: Optional[str] = None,
                               **extra: Any) -> Any:
        body = {"amount": str(amount), "currency": currency, "title": title}
        body.update(extra)
        return self.request(
            "POST",
            f"/api/v1/stores/{self._store(store_id)}/payment-requests",
            body,
        )

    def create_payout(self, destination: str, amount: str,
                      payment_method: Optional[str] = None,
                      store_id: Optional[str] = None, **extra: Any) -> Any:
        # payment_method=None auto-selects an enabled method (Lightning first).
        # NOTE: `destination` must match it — a BOLT11 invoice / LN address for
        # BTC-LN, an on-chain address for BTC-CHAIN. Pass payment_method
        # explicitly if your destination isn't Lightning.
        # The id goes in `payoutMethodId` (current BTCPay); the legacy
        # `paymentMethod` name is silently ignored on new instances, so we send
        # both for forward/backward compatibility. See refund_invoice for why.
        pm = self.resolve_payment_method(payment_method, store_id=store_id)
        body = {"destination": destination, "amount": str(amount),
                "payoutMethodId": pm, "paymentMethod": pm}
        body.update(extra)
        return self.request(
            "POST", f"/api/v1/stores/{self._store(store_id)}/payouts", body
        )
