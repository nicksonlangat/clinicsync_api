from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderItem


# Disable signal during certain operations to prevent recursion
def disable_signals():
    post_save.disconnect(update_order_status, sender=OrderItem)
    post_save.disconnect(mark_order_items_received, sender=Order)


def enable_signals():
    post_save.connect(update_order_status, sender=OrderItem)
    post_save.connect(mark_order_items_received, sender=Order)


@receiver(post_save, sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    if order.items.filter(status=OrderItem.Status.PENDING).exists():
        if order.status == Order.Status.COMPLETE:
            order.status = Order.Status.PENDING
            order.save()
        return
    # If all items are received, update the status of the order to Complete
    order.status = Order.Status.COMPLETE
    order.save()


@receiver(post_save, sender=Order)
def mark_order_items_received(sender, instance, **kwargs):
    if instance.status == Order.Status.COMPLETE:
        # Disable signal to prevent recursion
        disable_signals()
        order_items = instance.items.all()
        for order_item in order_items:
            order_item.status = OrderItem.Status.RECEIVED
            order_item.save()
        # Enable signal after performing the operation
        enable_signals()

    if (
        instance.status == Order.Status.PENDING
        or instance.status == Order.Status.CANCELLED
    ):
        # Disable signal to prevent recursion
        disable_signals()
        order_items = instance.items.all()
        for order_item in order_items:
            order_item.status = OrderItem.Status.PENDING
            order_item.save()
        # Enable signal after performing the operation
        enable_signals()
