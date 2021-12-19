import pandas as pd
from bs4 import BeautifulSoup
import requests


class StonkMedia:

    def __init__(self, stonk):
        self.stonk = stonk
        self.url = f"https://finviz.com/quote.ashx?t={stonk}"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.html = None

    def scrape_page_html(self):
        page = requests.get(self.url, headers=self.headers)
        data = page.content
        return BeautifulSoup(data, 'html.parser')

    def parse_news(self):
        if not self.html:
            self.html = self.scrape_page_html()
        news = pd.read_html(str(self.html), attrs={'class': 'fullview-news-outer'})[0]
        links = []
        for a in self.html.find_all('a', class_="tab-link-news"):
            links.append(a['href'])

        news.columns = ['Date', 'News Headline']
        news['Article Link'] = links
        news = news.set_index('Date')
        return news

    def parse_insiders(self):
        if not self.html:
            self.html = self.scrape_page_html()
        insider = pd.read_html(str(self.html), attrs={'class': 'body-table'})[0]

        insider = insider.iloc[1:]
        insider.columns = ['Trader', 'Relationship', 'Date', 'Transaction',
                           'Cost', '# Shares', 'Value ($)', '# Shares Total',
                           'SEC Form 4']
        insider = insider[insider.columns]
        insider = insider.set_index('Date')
        return insider
