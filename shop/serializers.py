from rest_framework import serializers
from .models import *


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "get_absolute_url",
            "description",
            "price",
            "get_image",
            "get_thumbnail",
            "image",
        )


class ImageSerializer(serializers.ModelSerializer):
    # product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = ProductImages
        fields = ["id", "get_image", "product", "image"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class ItemsOrderedSerializer(serializers.ModelSerializer):
    product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = ItemOrdered
        fields = "__all__"

class CreateItemsOrderedSerializer(serializers.ModelSerializer):
    # product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = ItemOrdered
        fields = "__all__"