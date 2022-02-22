from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from .paypal_calls import *
from decouple import config
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
import pycountry
import json
# Create your views here.


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        print(SAFE_METHODS)
        return request.method in SAFE_METHODS


class CapturePay(APIView):
    def post(self, request, format=None):
        id = request.data['id']
        capture_order(id)
        return Response("OK")


class RegisterOrder(APIView, DestroyModelMixin):
    queryset = Order.objects.all()
    # permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = OrderSerializer

    def post(self, request, format=None):

        id = request.data['id']
        data = get_order(id).result
        address = data.purchase_units[0].shipping.address
        # print(data.purchase_units[0].contact_value)
        serializer = OrderSerializer(data={
            'order_id': id,
            'state': address.admin_area_2,
            'adress_line': address.address_line_1,
            'paid': True,
            'full_name': data.purchase_units[0].shipping.name.full_name,
            'country': pycountry.countries.get(alpha_2=address.country_code).name.lower(),
            'zip_code': address.postal_code,
            'contact_email': data.purchase_units[0].payee.email_address
            # 'city':

        })

        if serializer.is_valid():
            order = serializer.save()
            for item in data.purchase_units[0].items:
                items_ordered_serializer = CreateItemsOrderedSerializer(data={
                    'amount': item.quantity,
                    'order': order.order_id,
                    'product': item.sku


                })
                if items_ordered_serializer.is_valid():
                    items_ordered_serializer.save()
                else:
                    print(items_ordered_serializer.errors)
        else:
            print(serializer.errors)

        # Orders.new()
        return Response("OK")


class CreatePayLink(APIView):

    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated|ReadOnly]

    def post(self, request, format=None):
        paypal_link = create_order(request.data)
        # print(request.data)

        return Response({"paypal_link": paypal_link})


class DecksViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = DeckSerializer
    queryset = Product.objects.all()
    parser_classes = (MultiPartParser,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', ]
    model = Product

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     # serializer = self.get_serializer(data=request.data)
    #     # serializer.is_valid(raise_exception=True)
    #     # self.perform_create(serializer)
    #     # headers = self.get_success_headers(serializer.data)
    #     return Response("OK")

    # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-created_at")
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # parser_classes = (MultiPartParser,)
    filter_fields = ('order_id', "country", "status")
    search_fields = ('full_name', 'contact_email')

    model = Order

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            order_id = self.request.query_params.get('order_id')
            if order_id is not None:
                permission_classes = [ReadOnly]
            else:
                permission_classes = [IsAuthenticated]

                # permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ItemsOrderedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = ItemsOrderedSerializer
    queryset = ItemOrdered.objects.all()
    # parser_classes = (MultiPartParser,)
    model = ItemOrdered

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = ItemOrdered.objects.all()
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        return queryset

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ProductImagesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = ImageSerializer
    # queryset = ProductImages.objects.all()
    parser_classes = (MultiPartParser,)
    model = ProductImages

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = ProductImages.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id is not None:
            queryset = queryset.filter(product=product_id)
        return queryset

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data_list = []
        new_data = dict(request.data)
        # print(request.data)
        if len(request.data) != 0:
            for x, y in zip(new_data['image'], new_data['product']):
                data_list.append({'image': x, 'product': y})
        # # print(dict(request.data)['product'])
        serializer = self.get_serializer(data=data_list, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = Category_serializer
    queryset = Category.objects.all()
    # filter_backends = (DjangoFilterBackend,)
    # filter_fields = ("category",)
    # parser_classes = (MultiPartParser,)
    model = Category
