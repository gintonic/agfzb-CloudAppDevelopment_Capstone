from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://bb538f6a.us-south.apigw.appdomain.cloud/dealership"
        # Get dealers from the URL
        context['dealerships'] = get_dealers_from_cf(url)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://bb538f6a.us-south.apigw.appdomain.cloud/review"
        context['reviews'] = get_dealer_reviews_from_cf(url, dealer_id)
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    user = request.user
    context = dict()
    context["cars"] = CarModel.objects.all()
    if user.is_authenticated:
        if request.method == "GET":
            url = "https://bb538f6a.us-south.apigw.appdomain.cloud/dealership"
            context['dealer'] = get_dealer_by_id(url, dealer_id)

            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == "POST":
            review = dict()
            review["dealership"] = dealer_id
            review["name"] = user.username
            if request.POST['content'] == "on":
                review["purchase"] = True
            else:
                review["purchase"] = False
    
            review["review"] = request.POST['content']

            date = request.POST["purchasedate"].split("/")
            review["purchase_date"] = datetime(month=int(date[0]), day=int(date[0]), year=int(date[2])).isoformat()
            
            car_selected = context["cars"][int(request.POST['car'])]
            review["car_make"] = car_selected.carMake.name
            review["car_model"] = car_selected.name
            review["car_year"] = car_selected.year.strftime("%Y")

            json_payload = dict()
            json_payload["review"] = review

            url="https://bb538f6a.us-south.apigw.appdomain.cloud/review"
            response = post_request(url, json_payload, dealerId=dealer_id)
            return HttpResponse(response)
            # return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

