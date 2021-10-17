from decouple import config
from django.http import request
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS,AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from paypalcheckoutsdk.orders import OrdersGetRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest, OrdersCreateRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalhttp import HttpError
from decouple import config
import pycountry
import json
# Create your views here.


def create_order(data, debug=False):
    billing = data['billing']
    items = data['cart']['items']
    items_data = []
    total = 0
    state = ""
    if billing["state"] != None and billing["state"] != "":
        state = billing["state"]
    else:
        state = billing["country"]

    for item in items:
        item_object = {
            "name": item['title'],
            "description": item['description'],
            "sku": item['id'],
            "unit_amount": {
                "currency_code": "USD",
                "value": item['price']
            },
            "quantity": f"{item['amount']}",
                        "category": "PHYSICAL_GOODS"
        }
        total += float(item['price']) * float(item['amount'])
        items_data.append(item_object)
    request_body = (
        {
            "intent": "CAPTURE",
            "application_context": {
                "return_url": "http://localhost:8080/payment_successful",
                "cancel_url": "https://www.example.com",
                "brand_name": "School of Magic",
                "landing_page": "BILLING",
                "shipping_preference": "SET_PROVIDED_ADDRESS",
                "user_action": "CONTINUE",
            },
            "purchase_units": [
                {
                "payee": {
                "email_address": str(billing['email']),
                },
            
                    # "reference_id": "PUHF",
                    # "description": "Sporting Goods",

                    # "custom_id": "CUST-HighFashions",
                    # "soft_descriptor": "HighFashions",
                   
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{total}",
                        "breakdown": {
                            "item_total": {
                                "currency_code": "USD",
                                "value": f"{total}"
                            },
                        },
                    },


                    "items":
                    items_data,
                    "shipping": {
                        # "method": "United States Postal Service",
                        "name": {
                            "full_name": billing['name']
                        },
                        "address": {
                            "address_line_1": billing['address_line'],
                            # "address_line_2": billing['address_line'],

                            # "admin_area_1": billing['state'],
                            "admin_area_2": state,
                            "postal_code": billing['zip_code'],
                            "country_code": pycountry.countries.get(name=billing['country']).alpha_2
                        }
                    }
                }
            ]
        }
    )
    # print(request_body)

    client_id = config("PAYPAL_ID")
    client_secret = config("PAYPAL_SECRET")
# Creating an environment
    environment = SandboxEnvironment(
        client_id=client_id, client_secret=client_secret)
    client = PayPalHttpClient(environment)
    request = OrdersCreateRequest()
    request.headers['prefer'] = 'return=representation'
    request.request_body(request_body)
    response = client.execute(request)
    if debug:
        print('Status Code: ', response.status_code)
        print('Status: ', response.result.status)
        print('Order ID: ', response.result.id)
        print('Intent: ', response.result.intent)
        print('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(
                link.rel, link.href, link.method))
            print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                               response.result.purchase_units[0].amount.value))
            # json_data = response.result
            # print ("json_data: ", json.dumps(json_data,indent=4))
    # print(response.result.links[1].href)
    return response.result.links[1].href


def get_order(order_id):
    # """Method to get order"""
    client_id = config("PAYPAL_ID")
    client_secret = config("PAYPAL_SECRET")
# Creating an environment
    environment = SandboxEnvironment(
        client_id=client_id, client_secret=client_secret)
    client = PayPalHttpClient(environment)
    request = OrdersGetRequest(order_id)
    response = client.execute(request)
    for link in response.result.links:
        print('\t{}: {}\tCall Type: {}'.format(
            link.rel, link.href, link.method))
    print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                       response.result.purchase_units[0].amount.value))
    # print(json.dumps(response.result))
    # print(response.result.purchase_units[0].items)
    # for x in response.result.purchase_units[0].items:
    #     print(x.name)
    # # json_data = object_to_json(response.result)
    # print("json_data: ", json.dumps(json_data, indent=4))
    return response


def capture_order(id):
    client_id = config("PAYPAL_ID")
    client_secret = config("PAYPAL_SECRET")
# Creating an environment
    environment = SandboxEnvironment(
        client_id=client_id, client_secret=client_secret)
    client = PayPalHttpClient(environment)
    request = OrdersCaptureRequest(id)
    request.headers['prefer'] = 'return=representation'

    try:
        # Call API with your client and get a response for your call
        response = client.execute(request)

    # If call returns body in response, you can get the deserialized version from the result attribute of the response
        order = response.result.id
    except IOError as ioe:
        if isinstance(ioe, HttpError):
            # Something went wrong server-side
            print(ioe.status_code)
            print(ioe.headers)
            print(ioe)
        else:
            # Something went wrong client side
            print(ioe)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        print(SAFE_METHODS)
        return request.method in SAFE_METHODS




class CapturePay(APIView):
    def post(self, request, format=None):
        id = request.data['id']
        capture_order(id)
        return Response("OK")


class RegisterOrder(APIView,DestroyModelMixin):
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
            'country': pycountry.countries.get(alpha_2=address.country_code).name,
            'zip_code': address.postal_code,
            'contact_email':data.purchase_units[0].payee.email_address
            # 'city':

        })

        if serializer.is_valid():
            order =serializer.save()
            for item in data.purchase_units[0].items:
                items_ordered_serializer = CreateItemsOrderedSerializer(data={
                'amount':item.quantity,
                'order':order.order_id,
                'product':item.sku
                
              
            })
                if items_ordered_serializer.is_valid():
                    items_ordered_serializer.save()
                else :
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
    permission_classes = [IsAuthenticated | ReadOnly]
    serializer_class = DeckSerializer
    queryset = Product.objects.all()
    parser_classes = (MultiPartParser,)
    model = Product

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated|ReadOnly]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    # parser_classes = (MultiPartParser,)
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Order.objects.all()
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        return queryset
    model = Order
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]


class ItemsOrderedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated|ReadOnly]
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
    permission_classes = [IsAuthenticated|ReadOnly]
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
            # print(x,y)
                data_list.append({'image': x, 'product': y})
        # # print(dict(request.data)['product'])
        serializer = self.get_serializer(data=data_list, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # return Response()
        # # for x, y in zip(new_data['image'], new_data['product']):
        # #     # print(x,y)
        # #     data_list.append({'image': x, 'product': y})
        # # # # print(dict(request.data)['product'])
        # # serializer = self.get_serializer(data=data_list, many=True)
        # # serializer.is_valid(raise_exception=True)
        # # self.perform_create(serializer)
        # # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
