from django.shortcuts import render
from pya3 import *
import pymongo
from pymongo import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from threading import Thread



@login_required
def home(request):
    client = pymongo.MongoClient("mongodb+srv://aaush:AaushMongoTestAccount@gopassive.niccs6s.mongodb.net/?retryWrites=true&w=majority")

    db = client['lowHighTrends']
    collection = db['inputData']
    doc_id = "NIFTY_LPL_LPH_DETAILS"
    filter_query = {'_id': doc_id}


    if request.method == "POST":
        print("-----------------------------------------------------------------POSTDATA_--------------------------------")
        inputData = dict(request.POST)
        print(inputData)
        data = {
            "_id":"NIFTY_LPL_LPH_DETAILS",
        "instrument" : inputData['selectedInstrument'][0],
        "triggerLevel" : int(inputData['triggerLevel'][0]),
        "selectedFeature" : inputData['selectedFeature'][0],
        "entryType":inputData['selectedFeature'][0],
        "stoploss": inputData['stoploss'][0],
        "lots": inputData['lots'][0],
        "strategyStatus": inputData['strategyStatus'][0],
        "stoplossStatus": "INACTIVE",
        "stoploss_value_LPH": None,
        "stoploss_value_LPL": None,
        }
        print("DATA:::::",data)
        try:
            collection.insert_one(data)
        except:
            filter_query = {'_id': "NIFTY_LPL_LPH_DETAILS"}
            update_query = {'$set':{
            "instrument" : inputData['selectedInstrument'][0],
            "triggerLevel" : int(inputData['triggerLevel'][0]),
            "selectedFeature" : inputData['selectedFeature'][0],
            "entryType":inputData['selectedFeature'][0],
            "stoploss": inputData['stoploss'][0],
            "lots": inputData['lots'][0],
            "strategyStatus": inputData['strategyStatus'][0],
            "stoplossStatus": "INACTIVE",
            "stoploss_value_LPH": None,
            "stoploss_value_LPL": None,
            "immediateStop": True,
            }}
            result = collection.update_one(filter_query, update_query)
        
        sleep(5)
        from .strategyLogic import main
        thread = Thread(target=main)
        thread.start()

        status = collection.find_one(filter_query)['status'].upper()
        print("STATUS",status)
        return render(request,"app/home.html",{"status":status})

    status = collection.find_one(filter_query)['status'].upper()
    print("STATUS",status)
    return render(request,"app/home.html",{"status":status})


def stopStrategy(request):
    client = pymongo.MongoClient("mongodb+srv://aaush:AaushMongoTestAccount@gopassive.niccs6s.mongodb.net/?retryWrites=true&w=majority")
    db = client['lowHighTrends']
    collection = db['inputData']

    doc_id = "NIFTY_LPL_LPH_DETAILS"
    filter_query = {'_id': doc_id}
    update_query = {'$set': {"immediateStop": True}}
    result = collection.update_one(filter_query, update_query)
    print(result)
    print("STOPPING THE STRATEGY")
    return redirect('home')



from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import SignUp
from django.contrib.auth import login, authenticate
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            print("VALID")
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid username or password. Please try again."
            print(error_message)
            return render(request, 'app/login.html', {'error_message': error_message})
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
def user_signup(request):
    # if request.method == 'POST':
    #     print("REQUEST TO CREATE USER")
    #     username = request.POST['username']
    #     email = request.POST['email']
    #     password1 = request.POST['password1']
    #     password2 = request.POST['password2']

    #     if password1 != password2:
    #         error_message = "Confirm Password and Password should be the same."
    #         print(error_message)
    #         return render(request, 'app/signup.html', {'error_message': error_message})
    #     else:
    #         # Check if a user with the provided username or email already exists
    #         if User.objects.filter(username=username).exists():
    #             error_message = "User already exists with the provided username!"
    #             return render(request, 'app/signup.html', {'error_message': error_message})

    #         # Create the user using Django's built-in User model
    #         user = User.objects.create_user(username=username, email=email, password=password1)
    #         user.save()

    #         # Authenticate and log in the user
    #         user = authenticate(username=username, password=password1)
    #         if user is not None:
    #             login(request, user)

    #         return redirect('login')
    # else:
    #     return render(request, 'app/signup.html')
    print("SIGNUP PAGE IS TRIGGERED, BUT CURRENTLY IT DOES NOT WORK!")
    return render(request, 'app/signup.html')
    


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    print("LOGOUT USER!!")
    return redirect('login') 

def userDetails(request):
    client = pymongo.MongoClient("mongodb+srv://aaush:AaushMongoTestAccount@gopassive.niccs6s.mongodb.net/?retryWrites=true&w=majority")
    db = client['lowHighTrends']
    collection = db['userCredentials']
    doc_id = "LPL_LPH_USER_CREDS"
    query = {"_id": doc_id}
    user_id = collection.find_one(query)['userId']

    if request.method == 'POST':
        print(request.POST)
        inputData = dict(request.POST)
        new_userId = inputData['username'][0]
        new_apikey = inputData['apiKey'][0]
        query = {'_id': doc_id}
        update_query = {
        "$set": {
            "api_key": new_apikey,
            "userId": new_userId
        }
    }
        collection.update_one(query, update_query)
        client.close()
        return redirect('home')

    client.close()

    print("USERDETAILS ASKED!!")
    return render(request, 'app/userDetails.html',{'user_id':user_id})
