from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Category, Clinic, Product, Vendor


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
