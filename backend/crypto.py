import datetime as dt
import yfinance_ez as yf
from flask import url_for

from backend.backend import fix_dataframe


class Crypto:
    def __init__(self, crypto: str):
        self.name = crypto
        self.yf_crypto = yf.Ticker(self.name)
        self.hist = self.yf_crypto.get_history(period=yf.TimePeriods.FiveYears)
        self.financials_data = self.yf_crypto.financials_data
        self.fundamentals_data = self.yf_crypto.fundamentals_data
        # self.logo = url_for('static', filename=f"assets/img/crypto_logos/{self.name}.png")
        self.price_history = self.price_history()

    def __eq__(self, other):
        return self.name == other.name

    def price_history(self) -> dict:
        dec_place = 2
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime.now()
        data = self.yf_crypto.get_history(start=start, end=end)
        data = fix_dataframe(data)

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
