import nltk
from bs4 import BeautifulSoup
import requests
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# nltk.download('vader_lexicon')

def get_stock_data(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract stock price
    price = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text

    # Extract stock volume
    volume = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'}).text


    return price, volume

ticker = 'AAPL'


def get_news_headlines(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}/news'
    # url2 = f''
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup.find_all('h3', class_='clamp yf-1044anq'))

    headlines = []
    for item in soup.find_all('h3', class_='clamp yf-1044anq'):
        headlines.append(item.get_text(strip=True))


    return headlines



sia = SentimentIntensityAnalyzer()

def analyze_headlines(headlines):
    sentiment_scores = [sia.polarity_scores(headline) for headline in headlines]
    return sentiment_scores





class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("Window.ui", self)
        self.show()

    def on_Submit_btn_pressed(self):
        text_input = self.findChild(QLineEdit, "ticker_entry")
        text_output = self.findChild(QTextBrowser,"output_details")

        if(text_input.text() != ''):
            ticker = text_input.text()
        else:
            ticker = "AAPL"
        # print(ticker)
        price, volume = get_stock_data(ticker)
        # print(price, volume)

        text_output.setText(ticker)
        text_output.append(f"{ticker} Stock Price: {price}")
        text_output.append(f"{ticker} Trading Volume: {volume}")
        # print(f"{ticker} Trading Volume: {volume}")


        # Aggregate the compound scores
        headlines = get_news_headlines(ticker)
        sentiment_scores = analyze_headlines(headlines)

        total_compound = sum(score['compound'] for score in sentiment_scores)
        average_compound = total_compound / len(sentiment_scores)

        # print(f"Total Compound Sentiment Score: {total_compound:.3f}")
        text_output.append(f"Average Compound Sentiment Score: {average_compound:.3f}")

        if average_compound >= 0.75:
            sentiment = "Very Positive"
        elif 0.05 <= average_compound < 0.75:
            sentiment = "Positive"
        elif -0.05 < average_compound < 0.05:
            sentiment = "Neutral"
        elif -0.75 <= average_compound <= -0.05:
            sentiment = "Negative"
        else:  # average_compound < -0.75
            sentiment = "Very Negative"

        text_output.append(f"Overall Sentiment: {sentiment}")

    def on_Visualize_btn_pressed(self):
        text_input = self.findChild(QLineEdit, "ticker_entry")

        if (text_input.text() != ''):
            global ticker
            ticker = text_input.text()
        else:
            ticker = "AAPL"

        headlines = get_news_headlines(ticker)
        sentiment_scores = analyze_headlines(headlines)

        compound_scores = [score['compound'] for score in sentiment_scores]
        current_date = datetime.now()
        dates = pd.date_range(end=current_date, periods=len(compound_scores), freq="ME")

        plt.plot(dates, compound_scores, marker='o')
        plt.title(f'Sentiment Analysis of {ticker} News Headlines')
        plt.xlabel('Date')
        plt.ylabel('Sentiment Score')
        plt.grid(True)
        plt.show()

def openWindow():
    app = QApplication([])
    window = Window()
    app.exec_()

openWindow()