import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "api_key" in kwargs:
            params=dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["language"] = kwargs["language"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url + "/v1/analyze", params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', kwargs["api_key"]))
        else:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})

        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        headers = {'content-type' : 'application/json'}
        response = requests.post(url, headers=headers, params=kwargs, json=json_payload["review"])
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealership"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id(url, dealerId):
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealer = json_result["dealership"][0]
        # Create a CarDealer object
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                short_name=dealer["short_name"],
                                st=dealer["st"], zip=dealer["zip"])
    return dealer_obj
# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["reviews"]
        # For each dealer object
        for review in reviews:
            # Create a CarDealer object
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                id=review["id"],
                review=review["review"],
                purchase_date=has_key_or_none("purchase_date", review),
                car_make=has_key_or_none("car_make", review),
                car_model=has_key_or_none("car_model", review),
                car_year=has_key_or_none("car_year", review),
                sentiment=analyze_review_sentiments(review["review"]))
            results.append(review_obj)

    return results

def has_key_or_none(key, my_dict):
    if key in my_dict:
        return my_dict[key]
    else:
        return ""

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(dealerreview): 
    url="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/234d471b-1eee-4b6f-bb79-a9f7da842d41"
    api_key="63LkmjfZhjsT0R5TJb1dlv3H8UkRmrwRwoUCWJaduo7s"
    version = "2020-08-01"
    features = "sentiment"
    language = "en"
    return_analyzed_text = True

    json_result = get_request(url, text=dealerreview, api_key=api_key, version=version, features=features, language=language,
        return_analyzed_text=return_analyzed_text)
    return json_result["sentiment"]["document"]["label"]
