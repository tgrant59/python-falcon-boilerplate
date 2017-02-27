import stripe
from app.utils import config

stripe.api_key = config.STRIPE_SECRET_KEY


def create_customer(email, metadata):
    return stripe.Customer.create(
        email=email,
        metadata=metadata
    )


def get_customer(customer_id):
    return stripe.Customer.retrieve(customer_id)


def update_customer_card(customer_id, source):
    customer = get_customer(customer_id)
    customer.source = source
    customer.save()
    return customer


def get_subscription(customer_id):
    subscriptions = stripe.Subscription.list(
        customer=customer_id
    )
    if len(subscriptions.data) >= 1:
        return subscriptions.data[0]
    return None


def create_or_update_subscription(customer_id, plan, had_trial, coupon_code=None):
    subscription = get_subscription(customer_id)
    if subscription:
        existing_sub = stripe.Subscription.retrieve(subscription["id"])
        existing_sub.plan = plan
        if had_trial:
            existing_sub.trial_end = "now"
        existing_sub.save()
        stripe.Invoice.create(
            customer=customer_id
        )
        return existing_sub
    coupon_id = None
    if coupon_code:
        coupon = retrieve_coupon_code(coupon_code)
        if coupon and coupon.valid:
            coupon_id = coupon.id
    new_sub = stripe.Subscription.create(
        customer=customer_id,
        plan=plan,
        coupon=coupon_id
    )
    if had_trial:
        new_sub.trial_end = "now"
        new_sub.save()
    return new_sub


def cancel_subscription(customer_id):
    subscription = get_subscription(customer_id)
    if subscription is not None:
        subscription_obj = stripe.Subscription.retrieve(subscription["id"])
        if subscription_obj.status != "trialing":
            subscription_obj.delete(at_period_end=True)
        return subscription_obj
    return None


def get_invoice(invoice_id):
    return stripe.Invoice.retrieve(invoice_id)


def get_invoice_history(customer_id, first_invoice, last_invoice):
    params = {
        "customer": customer_id
    }
    if first_invoice:
        params["ending_before"] = first_invoice
    if last_invoice:
        params["starting_after"] = last_invoice
    invoices = []
    for invoice in stripe.Invoice.list(**params):
        invoices.append({
            "id": invoice.id,
            "date": invoice.date,
            "paid": invoice.paid,
            "total": invoice.total
        })
    return invoices


def retrieve_coupon_code(coupon_code):
    try:
        return stripe.Coupon.retrieve(coupon_code)
    except stripe.InvalidRequestError:
        return None
