# CEO Request — F16 Chat Widget Sales Flow

Finalise the production-ready ChatWidget sales flow across product search, verified-build generation, build modification, cart, and lead capture.

The widget must render the owner's saved greeting, show truthful owner-inventory product cards, let a shopper add offered products to a private cart with editable quantities, let the shopper review and remove final cart items, and collect contact details only after the shopper explicitly signals buying intent from that final cart. The resulting lead must retain the final cart context.

Confirmed decisions:

* A cart does not reserve or decrement stock. It is a sales-inquiry list, not a checkout or order.
* A lead submission does not revalidate stock. It records an inquiry; it is not an order or purchase promise.
* Live internet product research is deferred.
* A verified build remains one recommendation card in chat. Selecting it adds its trusted individual component products to cart; the cart does not display or claim a verified-build bundle.
* Build generation and build modification remain deterministic and chat-led. A modified build never changes cart contents automatically.
* If a cart item is already part of the latest chat build, the cart prominently says so. The customer may keep or remove it.
* Quantities default to the quantity confidently requested in chat, otherwise one; every cart line is editable.
* The cart has an explicit `I want to buy` CTA. It opens contact/consent collection only for a non-empty final cart.
* After a successful lead, cart changes are unsent until the customer explicitly chooses `Update my request`. The same lead receives a new request version and the owner receives an updated notification.
* Customer checkout, payment collection, order creation, fulfilment, and shipping remain out of scope.

STATUS: CEO_REQUEST_RECORDED
