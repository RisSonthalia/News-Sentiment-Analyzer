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
from .models import SearchQueries,Review
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import ReviewForm
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

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
    # if request.user.is_anonymous:
    #     return redirect("/login")
    # else:
        query = "Featured News"
        cache_key = f"featured_news_{query}"
        cached_data = cache.get(cache_key)

        if cached_data:
            mylist, poscnt, neucnt, negcnt = cached_data
        else:
            mylist, poscnt, neucnt, negcnt = find_news(query)
            cache_timeout = getattr(settings, 'CACHE_TIMEOUT', DEFAULT_TIMEOUT)
            cache.set(cache_key, (mylist, poscnt, neucnt, negcnt), cache_timeout)

        context = {'mylist': mylist, 'poscnt': poscnt, 'negcnt': negcnt, 'neucnt': neucnt}
        return render(request, 'home.html', context)

def news_search(request):
    # if request.user.is_anonymous:
    #     return redirect("/login")
    # else:
        if request.method == 'GET':
            query = request.GET.get('query', '')
            if query:
                cache_key = f"search_results_{query}"
                cached_data = cache.get(cache_key)

                if cached_data:
                    mylist, poscnt, neucnt, negcnt = cached_data
                else:
                    mylist, poscnt, neucnt, negcnt = find_news(query)
                    cache_timeout = getattr(settings, 'CACHE_TIMEOUT', DEFAULT_TIMEOUT)
                    cache.set(cache_key, (mylist, poscnt, neucnt, negcnt), cache_timeout)

                    # Save the search data
                    if not request.user.is_anonymous:
                        search_query = SearchQueries(
                            user=request.user,
                            keyword=query,
                            positive_articles=poscnt,
                            negative_articles=neucnt,
                            neutral_articles=negcnt
                        )
                        search_query.save()

                context = {'mylist': mylist, 'query': query, 'poscnt': poscnt, 'negcnt': negcnt, 'neucnt': neucnt}
                return render(request, 'index.html', context)

        # If no query is provided, return the default news data
        return index(request)

def find_news(query):
                # API_KEY = "a2175caae9854461b90dcd24fb71f8f1"
                API_KEY = "86edec7c7cb347ba87deb4516cd66d79"
                url = "https://newsapi.org/v2/everything?q="
                # Get the news data
                try:
                    response = requests.get(f"{url}{query}&sortBy=popularity&apiKey={API_KEY}")
                    response.raise_for_status()
                    news = response.json()
                except requests.exceptions.RequestException as e:
                    print(e)
                    news = {'articles': []}  # Default to an empty list if there was an error

                articles = news.get('articles', [])
                
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
    
@login_required
def sentiment_analysis_view(request):
    user = request.user

    # Determine the filter based on the query parameter
    filter = request.GET.get('filter', 'today')
    now = timezone.now()

    if filter == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter == 'last_7_days':
        start_date = now - timedelta(days=7)
    else:
        start_date = None

    if start_date:
        if filter == 'yesterday':
            queries = SearchQueries.objects.filter(user=user, search_date__range=(start_date, end_date))
        else:
            queries = SearchQueries.objects.filter(user=user, search_date__gte=start_date)
    else:
        queries = SearchQueries.objects.filter(user=user)

    poscnt = queries.aggregate(Sum('positive_articles'))['positive_articles__sum'] or 0
    neucnt = queries.aggregate(Sum('neutral_articles'))['neutral_articles__sum'] or 0
    negcnt = queries.aggregate(Sum('negative_articles'))['negative_articles__sum'] or 0
    
   

    
    context = {
        'poscnt': poscnt,
        'neucnt': neucnt,
        'negcnt': negcnt,
        'filter': filter,
      
    }

    return render(request, 'sentiment_analysis.html', context)

def review_page(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user  # Assuming user is logged in
            new_review.save()
            return redirect('review_page')  # Redirect to the same page after submission
    else:
        form = ReviewForm()

   # Fetch reviews from database (assuming Review model exists)
    reviews = Review.objects.all()

    # Prepare star icons data
    for review in reviews:
        review.star_icons = range(review.stars)  # List of filled stars
        review.empty_star_icons = range(5 - review.stars)  # List of empty stars

    context = {
        'form': form,
        'reviews': reviews,
    }
    return render(request, 'review.html', context)
