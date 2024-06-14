import logging

from shared.email import TemplateEmail
from shared.pdf import Pdf

logger = logging.getLogger("django")


def generate_order_pdf(order, request):
    items = order.items.all()
    clinic = order.created_by.clinics.all()[0]

    selected_template = "order"

    pdf = Pdf().generate_pdf(
        request, selected_template, {"order": order, "items": items, "clinic": clinic}
    )
    return pdf.get()


def send_order_email_to_vendor(order, request):
    template = TemplateEmail(
        to=[order.vendor.email],
        subject="You have a new order",
        template="new_order",
        context={
            "items": order.items.all(),
            "order": order,
            "clinic": order.created_by.clinics.all()[0],
        },
        order_pdf=generate_order_pdf(order, request),
    )
    try:
        template.send()
        return True
    except Exception as e:
        logger.warning(f"Trouble emailing order {order.order_number}. Error is {e}")
        return False
