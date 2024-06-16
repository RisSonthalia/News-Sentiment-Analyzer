# NewsApp

## Introduction

NewsApp is a dynamic web application that aggregates the latest news articles and provides sentiment analysis on them. Built using Django, a high-level Python web framework, NewsApp offers users a seamless and robust platform to stay updated with current affairs while understanding the sentiment behind each news piece.

## Features

- **News Aggregation**: Fetches the latest news articles from various sources.
- **Sentiment Analysis**: Analyzes and categorizes news articles as Positive, Negative, or Neutral.
- **User Authentication**: Allows users to register, login, and manage their accounts.
- **Search Functionality**: Enables users to search for news articles based on keywords.
- **Responsive Design**: Ensures a seamless user experience across different devices.

## Live Demo

Check out the live demo of NewsApp [here](https://news-analyzer-two.vercel.app).

## Screenshots

Here are some screenshots of the NewsApp in action:

### Home Page
![Home Page](screenshots/homepage.png)

### Sentiment Analysis Results
![Sentiment Analysis](screenshots/screenshots.png)

## Getting Started

Follow these steps to set up and run the NewsApp on your local machine.

1. Clone the github repository.

2. Go to settings.py in the NewsAnalyzer/News and change 
   ALLOWED_HOSTS = [.vercel.app] 
   to ALLOWED_HOSTS = []

3. Go to NewsAnalyzer and bash these commands
   ```bash
   pip install virtualenv
    ```
   ```bash
   python -m venv myenv
   ```
   ```bash
   cd myen
   ```
   ```bash
   cd Scripts
   ```
   ```bash
   .\activate
   ```
    ```bash
   cd ../..
    ```
     ```bash
   pip install -r requirements.txt
   ```
   ```bash
   python manage.py migrate
   ```
    ```bash
   python manage.py runserver
   ```


### Prerequisites

Ensure you have the following installed on your system:

- Python (version 3.6 or higher)
- pip (Python package installer)
- Git

### How It Works

1. **News Aggregation**: News articles are fetched from various reputable sources using APIs.
2. **Sentiment Analysis**: Each article is analyzed using natural language processing (NLP) techniques to determine its sentiment.
3. **Categorization**: Articles are then categorized based on their sentiment:
   - **Positive**: Articles with a positive sentiment score.
   - **Negative**: Articles with a negative sentiment score.
   - **Neutral**: Articles with a neutral sentiment score.

### Sentiment Visualization

The sentiment analysis results are visualized using charts, providing a clear and immediate understanding of the sentiment distribution across the fetched news articles.

### Contributing
We welcome contributions to NewsApp! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.




