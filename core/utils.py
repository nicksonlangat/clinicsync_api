from shared.email import TemplateEmail


def send_order_email_to_vendor(order, order_items):
    print(order_items)
    template = TemplateEmail(
        to=[order.vendor.email],
        subject="You have a new order",
        template="new_order",
        # context={"code": code, "user": user},
    )
    try:
        template.send()
        return True
    except Exception:
        return False
