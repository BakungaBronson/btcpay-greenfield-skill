# BTCPay Greenfield — Permissions Reference

An API key carries a set of permission scopes. The golden rule from the BTCPay
docs: **give a key the minimum permissions it needs, and bind it to a single
store.** If a key only creates invoices, it should not be able to manage your
stores or move funds.

Create keys in the UI under `Account -> Manage account -> API keys`, or
programmatically via the Authorization flow (`/api-keys/authorize?...`).

> An API key created with **no** permissions has **unrestricted** access. Always
> pass an explicit permission list.

## Store-scoped form

Most store permissions can be limited to one store by appending the store id:

```
btcpay.store.cancreateinvoice:STORE_ID
```

Without the `:STORE_ID` suffix the permission applies to **every** store the
user owns.

## Recipe: typical eCommerce key (create invoices, refunds, webhooks)

```
btcpay.store.canviewinvoices
btcpay.store.cancreateinvoice
btcpay.store.canmodifyinvoices
btcpay.store.webhooks.canmodifywebhooks
btcpay.store.canviewstoresettings
btcpay.store.cancreatenonapprovedpullpayments
```

That last one is what lets you issue refunds (a refund creates a pull payment).

Optionally add `btcpay.user.canviewprofile` if you want `quickstart.py`'s
identity step (`GET /users/me`) to succeed — it's a profile read, not a store
permission, so it's left out of the minimal eCommerce set above. Without it the
quickstart simply skips that one step.

## Recipe: read-only monitoring key

```
btcpay.store.canviewinvoices
btcpay.store.canviewstoresettings
```

## Recipe: payouts / treasury (handle with care — moves money)

```
btcpay.store.canviewpayouts
btcpay.store.canmanagepayouts
btcpay.store.cancreatepullpayments
```

## Full permission list

### Store — invoices & payments
- `btcpay.store.canviewinvoices` — read invoices
- `btcpay.store.cancreateinvoice` — create invoices
- `btcpay.store.canmodifyinvoices` — update / mark / refund invoices
- `btcpay.store.canviewreports` — read reports
- `btcpay.store.canviewpaymentrequests`
- `btcpay.store.canmodifypaymentrequests`

### Store — settings & webhooks
- `btcpay.store.canviewstoresettings`
- `btcpay.store.canmodifystoresettings`
- `btcpay.store.webhooks.canmodifywebhooks`

### Store — pull payments & payouts (fund movement)
- `btcpay.store.canviewpullpayments`
- `btcpay.store.cancreatepullpayments`
- `btcpay.store.cancreatenonapprovedpullpayments` — needed for refunds
- `btcpay.store.canmanagepullpayments`
- `btcpay.store.canarchivepullpayments`
- `btcpay.store.canviewpayouts`
- `btcpay.store.canmanagepayouts`

### Store — Lightning
- `btcpay.store.cancreatelightninginvoice`
- `btcpay.store.canviewlightninginvoice`
- `btcpay.store.canuselightningnode`

### Store — offerings & subscriptions
- `btcpay.store.canviewofferings`
- `btcpay.store.canmodifyofferings`
- `btcpay.store.canmanagesubscribers`
- `btcpay.store.cancreditsubscribers`

### User / profile
- `btcpay.user.canviewprofile`
- `btcpay.user.canmodifyprofile`
- `btcpay.user.canviewnotificationsforuser`
- `btcpay.user.canmanagenotificationsforuser`
- `btcpay.user.candeleteuser`
- `btcpay.user.canmodifyserversettings`

### Server / admin (broad — avoid in app keys)
- `btcpay.server.canmodifyserversettings`
- `btcpay.server.canmanageusers`
- `btcpay.server.canviewusers`
- `btcpay.server.cancreateuser`
- `btcpay.server.canuseinternallightningnode`
- `btcpay.server.cancreatelightninginvoiceinternalnode`
- `btcpay.server.canviewlightninginvoiceinternalnode`
- `btcpay.impersonation.canimpersonate`

### Special
- `unrestricted` — everything. Only for throwaway testing, never production.

Each endpoint in `endpoints.md` lists the exact permission it requires under the
`Permission` column.
