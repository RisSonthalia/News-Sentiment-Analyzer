from django.shortcuts import render
import requests
from datetime import datetime
import pytz
from textblob import TextBlob
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import SignUpForm,UserLoginForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from .models import SearchQueries

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f'Welcome, {username}. Your account has been created!')
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def login_menu(request):
    if request.method == 'POST':
        form = UserLoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}.')
                return redirect('home')  # Replace 'home' with your desired URL name or path after login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('/')

def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Optionally, you can check if the email exists in your user database here
            # This is to ensure you're sending reset emails only to registered users
            subject = 'Password Reset Request'
            message = 'Please click the link below to reset your password:'
            from_email = settings.EMAIL_HOST_USER  # Use your own email configuration
            to_email = [email]
            send_mail(subject, message, from_email, to_email, fail_silently=True)
            messages.success(request, 'Password reset email sent. Please check your email.')
        else:
            messages.error(request, 'Invalid email. Please enter a valid email address.')
    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password.html', {'form': form})
    
def index(request):
#    if request.user.is_anonymous:
#         return redirect("/login")
#    else:
        query="Featured News"
        mylist,poscnt,neucnt,negcnt=find_news(query)
        context = {'mylist': mylist,'poscnt':poscnt,'negcnt':negcnt,'neucnt':neucnt}
        return render(request, 'home.html',context)

def news_search(request):
    # if request.user.is_anonymous:
    #    return redirect("/login")
    # else:
        if request.method == 'GET':
            query = request.GET.get('query', '')
            if query:
                mylist,poscnt,neucnt,negcnt=find_news(query)
                
                 # Save the search data
                search_query = SearchQueries(
                user=request.user,
                keyword=query,
                positive_articles=poscnt,
                negative_articles=neucnt,
                neutral_articles=negcnt
                )
                search_query.save()
        
                context = {'mylist': mylist,'query':query,'poscnt':poscnt,'negcnt':negcnt,'neucnt':neucnt}
                return render(request, 'index.html', context)
        # If no query is provided, return the default news data
        return index(request)

def find_news(query):
                API_KEY = "a2175caae9854461b90dcd24fb71f8f1"
                url = "https://newsapi.org/v2/everything?q="
                # Get the news data
                try:
                    response = requests.get(f"{url}{query}&sortBy=popularity&apiKey={API_KEY}")
                    response.raise_for_status()
                    india_news = response.json()
                except requests.exceptions.RequestException as e:
                    print(e)
                    india_news = {'articles': []}  # Default to an empty list if there was an error

                articles = india_news.get('articles', [])
                
                desc = []
                title = []
                img = []
                dates = []
                dates2 = []
                urls=[]
                sentiments = []
                pos_cnt=0
                neu_cnt=0
                neg_cnt=0
                

                # Extract data from the JSON response
                for article in articles:
                    if article.get('urlToImage', '') :
                        title_text = article.get('title', 'No Title')
                        desc_text = article.get('description', 'No Description')
                        combined_text = title_text + "." + desc_text

                        # Perform sentiment analysis
                        sentiment = classify_sentiment(combined_text)
                        if(sentiment=="Positive"):
                            pos_cnt=pos_cnt+1
                        elif(sentiment=="Negative"):
                            neg_cnt=neg_cnt+1
                        else:
                            neu_cnt=neu_cnt+1

                        title.append(title_text)
                        desc.append(desc_text)
                        img.append(article.get('urlToImage', ''))
                        dates.append(article.get('publishedAt', ''))
                        urls.append(article.get('url', ''))
                        sentiments.append(sentiment)
                    else:
                        continue

                # Convert and format dates
                for date_str in dates:
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                        date_obj = date_obj.replace(tzinfo=pytz.utc)
                        jakarta_tz = pytz.timezone("Asia/Jakarta")
                        date_obj_jakarta = date_obj.astimezone(jakarta_tz)
                        date_str_jakarta = date_obj_jakarta.strftime("%m/%d/%Y, %I:%M:%S %p")
                        dates2.append(date_str_jakarta)
                    else:
                        dates2.append("")
                        
                        
                        
                        sentiment=[]
                        
                # Create a list of tuples to pass to the context
                mylist = zip(title, desc, img, dates2,urls,sentiments)
                return mylist,pos_cnt,neu_cnt,neg_cnt
            
def classify_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"
    
