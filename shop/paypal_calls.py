from decouple import config


from paypalcheckoutsdk.orders import OrdersCaptureRequest, OrdersCreateRequest, OrdersGetRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalhttp import HttpError


def create_order(data, debug=False):
    billing = data['billing']
    items = data['cart']['items']
    items_data = []
    total = 0
    state = ""
    if billing["country"] != None and billing["country"] != "" and billing['country'] != "US":
        state = billing["country"]
    else:
        state = billing["state"]

    for item in items:
        item_object = {
            "name": item['title'],
            # "description": item['description'],
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
                "return_url": "https://school-of-magic.herokuapp.com/payment_successful",
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

                            "admin_area_1": state,
                            "admin_area_2": billing['city'],
                            "postal_code": billing['zip_code'],
                            "country_code": billing['country']
                        }
                    }
                }
            ]
        }
    )

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
