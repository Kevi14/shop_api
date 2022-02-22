import sys
from paypalcheckoutsdk.orders import OrdersGetRequest
import json
from paypalhttp.serializers.json_serializer import Json
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalhttp import HttpError
from decouple import config

# Creating Access Token for Sandbox
client_id = config("PAYPAL_ID")
client_secret = config("PAYPAL_SECRET")
# Creating an environment
environment = SandboxEnvironment(
    client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)

# request = OrdersCreateRequest()

# request.prefer('return=json')
items_data=[ {
                        "name": "T-Shirt",
                                "description": "Green XL",
                                "sku": "sku01",
                                "unit_amount": {
                                    "currency_code": "USD",
                                    "value": "100.00"
                                },
                        "quantity": "1",
                        "category": "PHYSICAL_GOODS"
                    },
                    {
                        "name": "Shoes",
                                "description": "Running, Size 10.5",
                                "sku": "sku02",
                                "unit_amount": {
                                    "currency_code": "USD",
                                    "value": "50.00"
                                },
                        "quantity": "2",
                        "category": "PHYSICAL_GOODS"
                    }]
request_body = (
    {
        "intent": "CAPTURE",
            "person":{
                    "emails":["kevikostandini@gmail.com"]
                },
            "emails":["kevikostandini@gmail.com"],
        "application_context": {
            "return_url": "https://www.example.com",
            "cancel_url": "https://www.example.com",
            "brand_name": "EXAMPLE INC",
            "landing_page": "BILLING",
            "shipping_preference": "SET_PROVIDED_ADDRESS",
            "user_action": "CONTINUE",
            "person":{
                    "emails":["kevikostandini@gmail.com"]
                },
            "emails":["kevikostandini@gmail.com"]
        },
        "purchase_units": [
            {
                "person":{
                    "emails":["kevikostandini@gmail.com"]
                },
                 "payee": {
                "email_address": "sb-@business.example.com",
                },
            
                
                "reference_id": "PUHF",
                "description": "Sporting Goods",

                "custom_id": "CUST-HighFashions",
                "soft_descriptor": "HighFashions",
                "contact_value":"a",
                "amount": {
                    "currency_code": "USD",
                    "value": "200.00",
                    "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value": "200.00"
                                },
                    },
                },


                "items":
                   items_data
                ,
                "shipping": {
                    "method": "United States Postal Service",
                    "name": {
                        "full_name": "John Doe"
                    },
                    "address": {
                        "address_line_1": "123 Townsend St",
                        "address_line_2": "Floor 6",
                        "admin_area_2": "San Francisco",
                        # "admin_area_1": "CA",
                        "postal_code": "94107",
                        "country_code": "US"
                    }
                }
            }
        ]
    }
)


def create_order(debug=False):
    request = OrdersCreateRequest()
    request.headers['prefer'] = 'return=representation'
    request.request_body(request_body)
    response = client.execute(request)
    if debug:
        print ('Status Code: ', response.status_code)
        print ('Status: ', response.result.status)
        print ('Order ID: ', response.result.id)
        print ('Intent: ', response.result.intent)
        print ('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
            print ('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                               response.result.purchase_units[0].amount.value))
            # json_data = response.result
            # print ("json_data: ", json.dumps(json_data,indent=4))
    print(response.result.links[1].href)

create_order(debug=True)

# # # Here, OrdersCaptureRequest() creates a POST request to /v2/checkout/orders
# # # Replace APPROVED-ORDER-ID with the actual approved order id.
# request = OrdersCaptureRequest("18N14302LC672841L")

# # try:
# #     # Call API with your client and get a response for your call
# #     response = client.execute(request)

# #     # If call returns body in response, you can get the deserialized version from the result attribute of the response
# #     order = response.result.id
# # except IOError as ioe:
# #     if isinstance(ioe, HttpError):
# #         # Something went wrong server-side
# #         print(ioe.status_code)
# #         print(ioe.headers)
# #         print(ioe)
# #     else:
# #         # Something went wrong client side
# #         print(ioe)
import json

def is_primittive(data):
    return isinstance(data, str) or isinstance(data, int)


def array_to_json_array(json_array):
    result = []
    if isinstance(json_array, list):
        for item in json_array:
            result.append(object_to_json(item) if not is_primittive(item)
                          else array_to_json_array(item) if isinstance(item, list) else item)
        return result


def object_to_json(json_data):
    """
    Function to print all json data in an organized readable manner
    """
    result = {}
    if sys.version_info[0] < 3:
        itr = json_data.__dict__.iteritems()
    else:
        itr = json_data.__dict__.items()
    for key, value in itr:
        # Skip internal attributes.
        if key.startswith("__") or key.startswith("_"):
            continue
        result[key] = array_to_json_array(value) if isinstance(value, list) else\
            object_to_json(value) if not is_primittive(value) else\
            value
    return result


def get_order(order_id):
    """Method to get order"""
    request = OrdersGetRequest(order_id)
    response = client.execute(request)
    data = response.result
    print('Status Code: ', response.status_code)
    print('Status: ', response.result.status)
    # Order_id
    print('Order ID: ', data.id)

    print('Intent: ', response.result.intent)
    print('Links:')
    for link in response.result.links:
        print('\t{}: {}\tCall Type: {}'.format(
            link.rel, link.href, link.method))
    print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                       response.result.purchase_units[0].amount.value))
    address = data.purchase_units[0].shipping.address
    print(address.address_line_1)
    # print(json.dumps(response.result))
    print(response.result.purchase_units[0].items)
    for x in response.result.purchase_units[0].items:
        print(x.name)
    json_data = object_to_json(response.result)

    print("json_data: ", json.dumps(json_data, indent=4))
    print(response.result.purchase_units[0].payee.email_address)

get_order("07030151XR390640P")
# import pycountry
# print(pycountry.countries.get(alpha_2="Al").name)
