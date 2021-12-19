import datetime as dt
import pandas as pd
import yfinance_ez as yf

from flask import url_for


class Crypto:
    def __init__(self, crypto: str):
        self.name = crypto
        self.yf_crypto = yf.Ticker(self.name)
        self.hist = self.yf_crypto.get_history(period=yf.TimePeriods.FiveYears)
        self.financials_data = self.yf_crypto.financials_data
        self.fundamentals_data = self.yf_crypto.fundamentals_data
        self.logo = url_for('static', filename=f"assets/img/crypto_logos/{self.name}.png")
        self.price_history = self.price_history()

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def fix_dataframe(d):
        d = d.reset_index(level=[0])
        d['Date'] = pd.to_datetime(d['Date']).apply(lambda x: x.date())
        return d

    def price_history(self) -> dict:
        dec_place = 2
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime.now()
        data = self.yf_crypto.get_history(start=start, end=end)
        data = self.fix_dataframe(data)

        open_price = [round(item, dec_place) for item in data['Open'].to_list()]
        close = [round(item, dec_place) for item in data['Close'].to_list()]
        # high = [round(item, dec_place) for item in data['High'].to_list()]
        # low = [round(item, dec_place) for item in data['Low'].to_list()]
        volume = [round(item, dec_place) for item in data['Volume'].to_list()]
        diff = [round(cl - op, dec_place) for op, cl in list(zip(open_price, close))]
        date_range = [item.strftime('%d %b %Y') for item in data['Date']]

        return {
            "open": open_price,
            "close": close,
            # "high": high,
            # "low": low,
            "volume": volume,
            "diff": diff,
            "date_range": date_range,
        }



    # def scrape_logo(self):
    #     logo_dict = {
    #         "LRC-USD": ("loopring", "lrc"),
    #         "BTC-USD": ("bitcoin", "btc")
    #     }
    #     url = f"https://cryptologos.cc/logos/{logo_dict[self.name][0]}-{logo_dict[self.name][1]}-logo.png"
    #     img_data = requests.get(url).content
    #     with open(url_for('static', filename=f'assets/img/{self.name}'), 'wb+') as handler:
    #         handler.write(img_data)
    #     return url_for('static', filename=f'assets/img/{self.name}')
