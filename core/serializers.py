from django.db.models import Sum
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import (
    Category,
    Clinic,
    Order,
    OrderItem,
    Patient,
    Product,
    Reservation,
    Staff,
    Vendor,
)
from .utils import send_order_email_to_vendor


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserSerializer(instance.created_by).data
        representation["members"] = UserSerializer(
            instance.members.all(), many=True
        ).data
        return representation


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_by"] = UserSerializer(instance.created_by).data
        return representation


class ProductSerializer(serializers.ModelSerializer):
    stock_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def get_stock_status(self, obj):
        if obj.stock_number <= 20 and obj.stock_number > 0:
            return "Low stock"
        if obj.stock_number == 0:
            return "Out of stock"
        return "In stock"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_by"] = UserSerializer(instance.created_by).data
        representation["category"] = CategorySerializer(instance.category).data
        representation["vendor"] = VendorSerializer(instance.vendor).data
        return representation


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.ListField(write_only=True)
    products = serializers.SerializerMethodField(read_only=True)
    all_products = serializers.SerializerMethodField(read_only=True)
    received_products = serializers.SerializerMethodField(read_only=True)
    order_totals = serializers.SerializerMethodField(read_only=True)
    reception_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def get_products(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_all_products(self, obj):
        return obj.items.all().count()

    def get_received_products(self, obj):
        return obj.items.filter(status="Received").count()

    def get_order_totals(self, obj):
        return obj.items.all().aggregate(total=Sum("total"))["total"]

    def get_reception_percentage(self, obj):
        total = obj.items.all().count()
        received = obj.items.filter(status="Received").count()
        percentage = f"{(received / total) * 100}%" if total else 0
        return percentage

    def update(self, instance, validated_data):
        new_order_items = [
            item["product"]
            for item in validated_data["order_items"]
            if "is_new" in item
        ]
        existing_order_items = [
            item for item in validated_data["order_items"] if "is_new" not in item
        ]

        for order_item in new_order_items:
            OrderItem.objects.create(
                order=instance,
                product=Product.objects.get(id=order_item["id"]),
                quantity=order_item["quantity"],
                price=order_item["price"],
            )

        for order_item in existing_order_items:
            saved_order_item = OrderItem.objects.get(id=order_item["id"])
            qty = order_item["quantity"]
            if int(qty) <= 0:
                saved_order_item.delete()
            else:
                saved_order_item.quantity = qty
                saved_order_item.save()

        instance.notes = validated_data.get("notes", instance.notes)
        instance.vendor = validated_data.get("vendor", instance.vendor)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Create and return a new `Order` instance, given the validated data.
        Also create related OrderItem instances.
        """
        order_items = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        request = self.context["request"]

        for order_item in order_items:
            OrderItem.objects.create(
                order=order,
                product=Product.objects.get(id=order_item["id"]),
                quantity=order_item["quantity"],
                price=order_item["price"],
            )
        email_sent = send_order_email_to_vendor(order, request)
        if email_sent:
            order.email_sent = True
            order.save()
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_by"] = UserSerializer(instance.created_by).data
        representation["vendor"] = VendorSerializer(instance.vendor).data
        return representation


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["product"] = ProductSerializer(instance.product).data
        return representation


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserSerializer(instance.user).data
        return representation


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_by"] = UserSerializer(instance.created_by).data
        representation["clinic"] = ClinicSerializer(instance.clinic).data
        return representation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_by"] = UserSerializer(instance.created_by).data
        representation["doctor"] = StaffSerializer(instance.doctor).data
        representation["patient"] = PatientSerializer(instance.patient).data
        return representation
