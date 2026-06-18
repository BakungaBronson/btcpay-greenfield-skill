# BTCPay Greenfield API — Full Endpoint Reference

Generated from the official OpenAPI spec (`/swagger/v1/swagger.json`). **195 endpoints** across 28 groups.

All paths are relative to your instance base URL, e.g. `https://your.btcpay.tld`. 
Auth header on every call: `Authorization: token <API_KEY>`.

The `perms` line is the permission scope the API key needs. Scope every key to the **minimum** set and to a **single store**.

> Tip: the most common eCommerce groups (Invoices, Webhooks, Stores, Payment Requests, Payouts) are listed first.


## Invoices

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/invoices` | Get invoices | `btcpay.store.canviewinvoices` |
| `POST` | `/api/v1/stores/{storeId}/invoices` | Create a new invoice | `btcpay.store.cancreateinvoice` |
| `DELETE` | `/api/v1/stores/{storeId}/invoices/{invoiceId}` | Archive invoice | `btcpay.store.canmodifyinvoices` |
| `GET` | `/api/v1/stores/{storeId}/invoices/{invoiceId}` | Get invoice | `btcpay.store.canviewinvoices` |
| `PUT` | `/api/v1/stores/{storeId}/invoices/{invoiceId}` | Update invoice | `btcpay.store.canmodifyinvoices` |
| `GET` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/payment-methods` | Get invoice payment methods | `btcpay.store.canviewinvoices` |
| `POST` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/payment-methods/{paymentMethodId}/activate` | Activate Payment Method | `btcpay.store.canviewinvoices` |
| `POST` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/refund` | Refund invoice | `btcpay.store.cancreatepullpayments` |
| `GET` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/refund/{paymentMethodId}` | Get invoice refund trigger data | `btcpay.store.cancreatepullpayments` |
| `POST` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/status` | Mark invoice status | `btcpay.store.canmodifyinvoices` |
| `POST` | `/api/v1/stores/{storeId}/invoices/{invoiceId}/unarchive` | Unarchive invoice | `btcpay.store.canmodifyinvoices` |

## Webhooks

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/webhooks` | Get webhooks of a store | `btcpay.store.webhooks.canmodifywebhooks` |
| `POST` | `/api/v1/stores/{storeId}/webhooks` | Create a new webhook | `btcpay.store.webhooks.canmodifywebhooks` |
| `DELETE` | `/api/v1/stores/{storeId}/webhooks/{webhookId}` | Delete a webhook | `btcpay.store.webhooks.canmodifywebhooks` |
| `GET` | `/api/v1/stores/{storeId}/webhooks/{webhookId}` | Get a webhook of a store | `btcpay.store.webhooks.canmodifywebhooks` |
| `PUT` | `/api/v1/stores/{storeId}/webhooks/{webhookId}` | Update a webhook | `btcpay.store.webhooks.canmodifywebhooks` |
| `GET` | `/api/v1/stores/{storeId}/webhooks/{webhookId}/deliveries` | Get latest deliveries | `btcpay.store.webhooks.canmodifywebhooks` |
| `GET` | `/api/v1/stores/{storeId}/webhooks/{webhookId}/deliveries/{deliveryId}` | Get a webhook delivery | `btcpay.store.webhooks.canmodifywebhooks` |
| `POST` | `/api/v1/stores/{storeId}/webhooks/{webhookId}/deliveries/{deliveryId}/redeliver` | Redeliver the delivery | `btcpay.store.webhooks.canmodifywebhooks` |
| `GET` | `/api/v1/stores/{storeId}/webhooks/{webhookId}/deliveries/{deliveryId}/request` | Get the delivery's request | `btcpay.store.webhooks.canmodifywebhooks` |

## Stores

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores` | Get stores | `btcpay.store.canviewstoresettings` |
| `POST` | `/api/v1/stores` | Create a new store | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}` | Remove Store | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}` | Get store | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}` | Update store | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/logo` | Deletes the store logo | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/logo` | Uploads a logo for the store | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/roles` | Get store's roles | `btcpay.store.canmodifystoresettings` |

## Payment Requests

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/payment-requests` | Get payment requests | `btcpay.store.canviewpaymentrequests` |
| `POST` | `/api/v1/stores/{storeId}/payment-requests` | Create a new payment request | `btcpay.store.canmodifypaymentrequests` |
| `DELETE` | `/api/v1/stores/{storeId}/payment-requests/{paymentRequestId}` | Archive payment request | `btcpay.store.canmodifypaymentrequests` |
| `GET` | `/api/v1/stores/{storeId}/payment-requests/{paymentRequestId}` | Get payment request | `btcpay.store.canviewpaymentrequests` |
| `PUT` | `/api/v1/stores/{storeId}/payment-requests/{paymentRequestId}` | Update payment request | `btcpay.store.canmodifypaymentrequests` |
| `POST` | `/api/v1/stores/{storeId}/payment-requests/{paymentRequestId}/pay` | Create a new invoice for the payment request | `btcpay.store.canviewpaymentrequests` |

## Stores (Payouts)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/payouts` | Get Store Payouts | `any authenticated` |
| `POST` | `/api/v1/stores/{storeId}/payouts` | Create Payout | `btcpay.store.cancreatenonapprovedpullpayments, btcpay.store.cancreatepullpayments` |
| `DELETE` | `/api/v1/stores/{storeId}/payouts/{payoutId}` | Cancel Payout | `btcpay.store.canmanagepullpayments` |
| `GET` | `/api/v1/stores/{storeId}/payouts/{payoutId}` | Get Payout | `btcpay.store.canmanagepullpayments` |
| `POST` | `/api/v1/stores/{storeId}/payouts/{payoutId}` | Approve Payout | `btcpay.store.canmanagepullpayments` |
| `POST` | `/api/v1/stores/{storeId}/payouts/{payoutId}/mark` | Mark Payout | `btcpay.store.canmanagepullpayments` |
| `POST` | `/api/v1/stores/{storeId}/payouts/{payoutId}/mark-paid` | Mark Payout as Paid | `btcpay.store.canmanagepullpayments` |

## Pull payments (Management)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/pull-payments` | Get store's pull payments | `btcpay.store.canmanagepullpayments` |
| `POST` | `/api/v1/stores/{storeId}/pull-payments` | Create a new pull payment | `btcpay.store.cancreatenonapprovedpullpayments, btcpay.store.cancreatepullpayments` |
| `DELETE` | `/api/v1/stores/{storeId}/pull-payments/{pullPaymentId}` | Archive a pull payment | `btcpay.store.canarchivepullpayments` |

## Pull payments (Public)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/pull-payments/{pullPaymentId}` | Get Pull Payment | `any authenticated` |
| `POST` | `/api/v1/pull-payments/{pullPaymentId}/boltcards` | Link a boltcard to a pull payment | `any authenticated` |
| `GET` | `/api/v1/pull-payments/{pullPaymentId}/lnurl` | Get Pull Payment LNURL details | `any authenticated` |
| `GET` | `/api/v1/pull-payments/{pullPaymentId}/payouts` | Get Payouts | `any authenticated` |
| `POST` | `/api/v1/pull-payments/{pullPaymentId}/payouts` | Create Payout | `any authenticated` |
| `GET` | `/api/v1/pull-payments/{pullPaymentId}/payouts/{payoutId}` | Get Payout | `any authenticated` |

## Store Wallet (On Chain)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet` | Get store on-chain wallet overview | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/address` | UnReserve last store on-chain wallet address | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/address` | Get store on-chain wallet address | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/feerate` | Get store on-chain wallet fee rate | `btcpay.store.canviewstoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/generate` | Generate store on-chain wallet | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/histogram` | Get store on-chain wallet balance histogram | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects` | Get store on-chain wallet objects | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects` | Add/Update store on-chain wallet objects | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects/{objectType}/{objectId}` | Remove store on-chain wallet objects | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects/{objectType}/{objectId}` | Get store on-chain wallet object | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects/{objectType}/{objectId}/links` | Add/Update store on-chain wallet object link | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/objects/{objectType}/{objectId}/links/{linkType}/{linkId}` | Remove store on-chain wallet object links | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/preview` | Preview store on-chain payment method addresses | `btcpay.store.canviewstoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/preview` | Preview proposed store on-chain payment method addresses | `btcpay.store.canviewstoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/transactions` | Get store on-chain wallet transactions | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/transactions` | Create store on-chain wallet transaction | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/transactions/broadcast` | Broadcast an on-chain transaction or finalized PSBT | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/transactions/{transactionId}` | Get store on-chain wallet transaction | `btcpay.store.canmodifystoresettings` |
| `PATCH` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/transactions/{transactionId}` | Patch store on-chain wallet transaction info | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}/wallet/utxos` | Get store on-chain wallet UTXOS | `btcpay.store.canmodifystoresettings` |

## Store (Payment Methods)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/payment-methods` | Get store payment methods | `btcpay.store.canviewstoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}` | Delete store's payment method | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}` | Get store payment method | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/payment-methods/{paymentMethodId}` | Update store's payment method | `btcpay.store.canmodifystoresettings` |

## Stores (Rates)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/rates` | Get rates | `btcpay.store.canviewstoresettings` |
| `POST` | `/api/v1/stores/{storeId}/rates/configuration/preview` | Preview rate configuration results | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/rates/configuration/{rateSource}` | Get store rate settings for the specified rate source | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/rates/configuration/{rateSource}` | Get store rate settings for the specified rate source | `btcpay.store.canmodifystoresettings` |

## Lightning (Store)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `POST` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/address` | Get deposit address | `btcpay.store.cancreatelightninginvoice` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/balance` | Get node balance | `btcpay.store.canuselightningnode` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/channels` | Get channels | `btcpay.store.cancreatelightninginvoice` |
| `POST` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/channels` | Open channel | `btcpay.store.cancreatelightninginvoice` |
| `POST` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/connect` | Connect to lightning node | `btcpay.store.cancreatelightninginvoice` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/histogram` | Get node balance histogram | `btcpay.store.canuselightningnode` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/info` | Get node information | `btcpay.store.canuselightningnode` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/invoices` | Get invoices | `btcpay.store.canviewlightninginvoice` |
| `POST` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/invoices` | Create lightning invoice | `btcpay.server.cancreatelightninginvoiceinternalnode` |
| `POST` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/invoices/pay` | Pay Lightning Invoice | `btcpay.store.cancreatelightninginvoice` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/invoices/{id}` | Get invoice | `btcpay.store.canviewlightninginvoice` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/payments` | Get payments | `btcpay.store.cancreatelightninginvoice` |
| `GET` | `/api/v1/stores/{storeId}/lightning/{cryptoCode}/payments/{paymentHash}` | Get payment | `btcpay.store.canuselightningnode` |

## Lightning address

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/lightning-addresses` | Get store configured lightning addresses | `btcpay.store.canviewstoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/lightning-addresses/{username}` | Remove configured lightning address | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/lightning-addresses/{username}` | Get store configured lightning address | `btcpay.store.canviewstoresettings` |
| `POST` | `/api/v1/stores/{storeId}/lightning-addresses/{username}` | Add or update store configured lightning address | `btcpay.store.canmodifystoresettings` |

## Apps

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/apps` | Get basic app data for all apps for all stores for a user | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/apps/crowdfund/{appId}` | Get crowdfund app data | `any authenticated` |
| `PUT` | `/api/v1/apps/crowdfund/{appId}` | Update a Crowdfund app | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/apps/pos/{appId}` | Get Point of Sale app data | `any authenticated` |
| `PUT` | `/api/v1/apps/pos/{appId}` | Update a Point of Sale app | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/apps/{appId}` | Delete app | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/apps/{appId}` | Get basic app data | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/apps/{appId}/image` | Uploads an image for an app item | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/apps/{appId}/image/{fileId}` | Deletes the app item image | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/apps/{appId}/sales` | Get app sales statistics | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/apps/{appId}/top-items` | Get app top items statistics | `btcpay.store.canmodifystoresettings` |
| `GET` | `/api/v1/stores/{storeId}/apps` | Get basic app data for all apps for a store | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/apps/crowdfund` | Create a new Crowdfund app | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/apps/pos` | Create a new Point of Sale app | `btcpay.store.canmodifystoresettings` |

## Subscriptions

| Method | Path | Summary | Permission |
|---|---|---|---|
| `POST` | `/api/v1/plan-checkout` | Create a plan checkout session | `btcpay.store.canmanagesubscribers` |
| `GET` | `/api/v1/plan-checkout/{checkoutId}` | Get a plan checkout | `any authenticated` |
| `POST` | `/api/v1/plan-checkout/{checkoutId}` | Proceed with a plan checkout | `any authenticated` |
| `GET` | `/api/v1/stores/{storeId}/offerings` | List offerings for a store | `btcpay.store.canviewofferings` |
| `POST` | `/api/v1/stores/{storeId}/offerings` | Create an offering | `btcpay.store.canmodifyofferings` |
| `GET` | `/api/v1/stores/{storeId}/offerings/{offeringId}` | Get an offering | `btcpay.store.canviewofferings` |
| `PUT` | `/api/v1/stores/{storeId}/offerings/{offeringId}` | Update an offering | `btcpay.store.canmodifyofferings` |
| `POST` | `/api/v1/stores/{storeId}/offerings/{offeringId}/plans` | Create an offering plan | `btcpay.store.canmodifyofferings` |
| `GET` | `/api/v1/stores/{storeId}/offerings/{offeringId}/plans/{planId}` | Get an offering plan | `btcpay.store.canviewofferings` |
| `PUT` | `/api/v1/stores/{storeId}/offerings/{offeringId}/plans/{planId}` | Update an offering plan | `btcpay.store.canmodifyofferings` |
| `DELETE` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}` | Delete a subscriber | `btcpay.store.canmanagesubscribers` |
| `GET` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}` | Get a subscriber | `btcpay.store.canviewofferings` |
| `GET` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}/credits/{currency}` | Get subscriber credit balance | `btcpay.store.canmanagesubscribers` |
| `POST` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}/credits/{currency}` | Update subscriber credit balance | `btcpay.store.cancreditsubscribers` |
| `PUT` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}/dates` | Update subscriber dates | `btcpay.store.canmanagesubscribers` |
| `POST` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}/suspend` | Suspend a subscriber | `btcpay.store.canmanagesubscribers` |
| `POST` | `/api/v1/stores/{storeId}/offerings/{offeringId}/subscribers/{customerSelector}/unsuspend` | Unsuspend a subscriber | `btcpay.store.canmanagesubscribers` |
| `POST` | `/api/v1/subscriber-portal` | Create a subscriber portal session | `btcpay.store.canmanagesubscribers` |
| `GET` | `/api/v1/subscriber-portal/{portalSessionId}` | Get a subscriber portal session | `any authenticated` |

## API Keys

| Method | Path | Summary | Permission |
|---|---|---|---|
| `POST` | `/api/v1/api-keys` | Create a new API Key | `unrestricted` |
| `DELETE` | `/api/v1/api-keys/current` | Revoke the current API Key | `any authenticated` |
| `GET` | `/api/v1/api-keys/current` | Get the current API Key information | `btcpay.server.canmanageusers` |
| `DELETE` | `/api/v1/api-keys/{apikey}` | Revoke an API Key | `unrestricted` |
| `POST` | `/api/v1/users/{idOrEmail}/api-keys` | Create a new API Key for a user | `btcpay.server.canmanageusers` |
| `DELETE` | `/api/v1/users/{idOrEmail}/api-keys/{apikey}` | Revoke an API Key of target user | `unrestricted` |

## Authorization

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api-keys/authorize` | Authorize User | `any authenticated` |

## Users

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/users` | Get all users | `btcpay.server.canviewusers` |
| `POST` | `/api/v1/users` | Create user | `btcpay.server.cancreateuser` |
| `DELETE` | `/api/v1/users/me` | Deletes user profile | `btcpay.user.candeleteuser` |
| `GET` | `/api/v1/users/me` | Get current user information | `btcpay.user.canviewprofile` |
| `PUT` | `/api/v1/users/me` | Update current user information | `btcpay.user.canmodifyprofile` |
| `DELETE` | `/api/v1/users/me/picture` | Deletes user profile picture | `btcpay.user.canmodifyprofile` |
| `POST` | `/api/v1/users/me/picture` | Uploads a profile picture for the current user | `btcpay.user.canmodifyprofile` |
| `DELETE` | `/api/v1/users/{idOrEmail}` | Delete user | `btcpay.user.candeleteuser` |
| `GET` | `/api/v1/users/{idOrEmail}` | Get user by ID or Email | `btcpay.server.canviewusers` |
| `POST` | `/api/v1/users/{idOrEmail}/approve` | Toggle user approval | `btcpay.user.canmodifyserversettings` |
| `POST` | `/api/v1/users/{idOrEmail}/lock` | Toggle user lock out | `btcpay.user.canmodifyserversettings` |

## Stores (Users)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/users` | Get store users | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/users` | Add a store user | `btcpay.store.canmodifystoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/users/{idOrEmail}` | Remove Store User | `btcpay.store.canmodifystoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/users/{idOrEmail}` | Updates a store user | `btcpay.store.canmodifystoresettings` |

## Stores (Email)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/email` | Get store email settings | `btcpay.store.canmodifystoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/email` | Update store email settings | `btcpay.store.canmodifystoresettings` |
| `POST` | `/api/v1/stores/{storeId}/email/send` | Send an email for a store | `btcpay.store.canmodifystoresettings` |

## Stores (Payout Processors)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/stores/{storeId}/payout-processors` | Get store configured payout processors | `btcpay.store.canviewstoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payout-processors/LightningAutomatedPayoutSenderFactory` | Get configured store Lightning automated payout processors | `btcpay.store.canviewstoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payout-processors/LightningAutomatedPayoutSenderFactory/{payoutMethodId}` | Get configured store Lightning automated payout processors | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/payout-processors/LightningAutomatedPayoutSenderFactory/{payoutMethodId}` | Update configured store Lightning automated payout processors | `btcpay.store.canviewstoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payout-processors/OnChainAutomatedPayoutSenderFactory/{paymentMethodId}` | Get configured store onchain automated payout processors | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/payout-processors/OnChainAutomatedPayoutSenderFactory/{paymentMethodId}` | Update configured store onchain automated payout processors | `btcpay.store.canviewstoresettings` |
| `GET` | `/api/v1/stores/{storeId}/payout-processors/OnChainAutomatedTransferSenderFactory` | Get configured store onchain automated payout processors | `btcpay.store.canviewstoresettings` |
| `PUT` | `/api/v1/stores/{storeId}/payout-processors/OnChainAutomatedTransferSenderFactory` | Update configured store onchain automated payout processors | `btcpay.store.canviewstoresettings` |
| `DELETE` | `/api/v1/stores/{storeId}/payout-processors/{processor}/{paymentMethodId}` | Remove store configured payout processor | `btcpay.store.canmodifystoresettings` |

## Payout Processors

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/payout-processors` | Get payout processors | `any authenticated` |

## Notifications (Current User)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/users/me/notification-settings` | Get notification settings | `btcpay.user.canmanagenotificationsforuser` |
| `PUT` | `/api/v1/users/me/notification-settings` | Update notification settings | `btcpay.user.canmanagenotificationsforuser` |
| `GET` | `/api/v1/users/me/notifications` | Get notifications | `btcpay.user.canmanagenotificationsforuser, btcpay.user.canviewnotificationsforuser` |
| `DELETE` | `/api/v1/users/me/notifications/{id}` | Remove Notification | `btcpay.user.canmanagenotificationsforuser` |
| `GET` | `/api/v1/users/me/notifications/{id}` | Get notification | `btcpay.user.canmanagenotificationsforuser, btcpay.user.canviewnotificationsforuser` |
| `PUT` | `/api/v1/users/me/notifications/{id}` | Update notification | `btcpay.user.canmanagenotificationsforuser` |

## Files

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/files` | Get all files | `btcpay.server.canmodifyserversettings` |
| `POST` | `/api/v1/files` | Uploads a file | `btcpay.server.canmodifyserversettings` |
| `DELETE` | `/api/v1/files/{fileId}` | Delete file | `btcpay.server.canmodifyserversettings` |
| `GET` | `/api/v1/files/{fileId}` | Get file | `btcpay.server.canmodifyserversettings` |

## ServerInfo

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/server/info` | Get server info | `any authenticated` |
| `GET` | `/api/v1/server/roles` | Get store's roles | `btcpay.server.canmodifyserversettings` |

## ServerEmail

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/server/email` | Get server email settings | `btcpay.server.canmodifyserversettings` |
| `PUT` | `/api/v1/server/email` | Update server email settings | `btcpay.server.canmodifyserversettings` |

## Health

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/api/v1/health` | Get health status | `any authenticated` |

## Miscelleneous

| Method | Path | Summary | Permission |
|---|---|---|---|
| `GET` | `/i/{invoiceId}` | Invoice checkout | `any authenticated` |
| `GET` | `/misc/lang` | Language codes | `any authenticated` |
| `GET` | `/misc/permissions` | Permissions metadata | `any authenticated` |
| `GET` | `/misc/rate-sources` | Get available rate sources | `any authenticated` |

## Lightning (Internal Node)

| Method | Path | Summary | Permission |
|---|---|---|---|
| `POST` | `/api/v1/server/lightning/{cryptoCode}/address` | Get deposit address | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/balance` | Get node balance | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/channels` | Get channels | `btcpay.server.canuseinternallightningnode` |
| `POST` | `/api/v1/server/lightning/{cryptoCode}/channels` | Open channel | `btcpay.server.canuseinternallightningnode` |
| `POST` | `/api/v1/server/lightning/{cryptoCode}/connect` | Connect to lightning node | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/histogram` | Get node balance histogram | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/info` | Get node information | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/invoices` | Get invoices | `btcpay.server.canviewlightninginvoiceinternalnode` |
| `POST` | `/api/v1/server/lightning/{cryptoCode}/invoices` | Create lightning invoice | `btcpay.server.cancreatelightninginvoiceinternalnode` |
| `POST` | `/api/v1/server/lightning/{cryptoCode}/invoices/pay` | Pay Lightning Invoice | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/invoices/{id}` | Get invoice | `btcpay.server.canviewlightninginvoiceinternalnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/payments` | Get payments | `btcpay.server.canuseinternallightningnode` |
| `GET` | `/api/v1/server/lightning/{cryptoCode}/payments/{paymentHash}` | Get payment | `btcpay.server.canuseinternallightningnode` |