
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
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
            "image",
            "category_id",
            "category"
        )

    # def create(self, validated_data):
    #     """
    #     We have a bit of extra checking around this in order to provide
    #     descriptive messages when something goes wrong, but this method is
    #     essentially just:

    #         return ExampleModel.objects.create(**validated_data)

    #     If there are many to many fields present on the instance then they
    #     cannot be set until the model is instantiated, in which case the
    #     implementation is like so:

    #         example_relationship = validated_data.pop('example_relationship')
    #         instance = ExampleModel.objects.create(**validated_data)
    #         instance.example_relationship = example_relationship
    #         return instance

    #     The default implementation also does not handle nested relationships.
    #     If you want to support writable nested relationships you'll need
    #     to write an explicit `.create()` method.
    #     """
    #     raise_errors_on_nested_writes('create', self, validated_data)

    #     print("+++++++++++++++++++++++++++++++++++++")
    #     print(validated_data['category'].category)
    #     # temp = Category.objects.get(category=validated_data['category'])
    #     # validated_data['category'] = temp
    #     # validated_data['category_id'] = temp

    #     ModelClass = self.Meta.model

    #     # Remove many-to-many relationships from validated_data.
    #     # They are not valid arguments to the default `.create()` method,
    #     # as they require that the instance has already been saved.
    #     info = model_meta.get_field_info(ModelClass)
    #     many_to_many = {}
    #     for field_name, relation_info in info.relations.items():
    #         if relation_info.to_many and (field_name in validated_data):
    #             many_to_many[field_name] = validated_data.pop(field_name)

    #     try:
    #         instance = ModelClass._default_manager.create(**validated_data)
    #     except TypeError:
    #         # tb = traceback.format_exc()
    #         msg = (
    #             'Got a `TypeError` when calling `%s.%s.create()`. '
    #             'This may be because you have a writable field on the '
    #             'serializer class that is not a valid argument to '
    #             '`%s.%s.create()`. You may need to make the field '
    #             'read-only, or override the %s.create() method to handle '
    #             'this correctly.\nOriginal exception was:\n %s' %
    #             (
    #                 ModelClass.__name__,
    #                 ModelClass._default_manager.name,
    #                 ModelClass.__name__,
    #                 ModelClass._default_manager.name,
    #                 self.__class__.__name__,
    #                 # tb
    #             )
    #         )
    #         raise TypeError(msg)

    #     # Save many-to-many relationships after the instance is created.
    #     if many_to_many:
    #         for field_name, value in many_to_many.items():
    #             field = getattr(instance, field_name)
    #             field.set(value)

    #     return instance


class ImageSerializer(serializers.ModelSerializer):
    # product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = ProductImages
        fields = ["id", "get_image", "product", "image"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class ClientOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("order_id", "created_at", "tracking_number",
                  "status", "contact_email")


class ItemsOrderedSerializer(serializers.ModelSerializer):
    product = DeckSerializer(many=False, read_only=True)
    order = ClientOrderSerializer(read_only=True)

    class Meta:
        model = ItemOrdered
        fields = "__all__"


class CreateItemsOrderedSerializer(serializers.ModelSerializer):
    # product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = ItemOrdered
        fields = "__all__"


class Category_serializer(serializers.ModelSerializer):
    # product = DeckSerializer(many=False, read_only=True)
    class Meta:
        model = Category
        fields = "__all__"
