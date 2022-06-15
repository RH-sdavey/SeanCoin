import datetime as dt

import yfinance_ez as yf

from backend.backend import fix_dataframe
from backend.lib import (
    company_columns, current_stock_columns, historical_stock_columns,
    financials_columns, holders_columns, logo_columns
)

earnings_keys = ["estimate", "actual", "date"]
financial_keys = ['date', 'revenue', 'earnings']


class Stonk:
    def __init__(self, stonk: str):
        self.name = stonk
        self.yf_stonk = yf.Ticker(self.name)
        self.hist = self.yf_stonk.get_history(period=yf.TimePeriods.FiveYears)
        self.price_history = self.price_history()
        try:
            self.q_earnings_data = {
                key: [item[key] for item in self.yf_stonk.financials_data['earnings']['earningsChart']['quarterly']]
                for key in earnings_keys
            }
            self.q_financial_data = {
                key: [item[key] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['quarterly']]
                for key in financial_keys
            }
            self.y_financial_data = {
                key: [item[key] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['yearly']]
                for key in financial_keys
            }

            self.dividends = self.yf_stonk.dividends.to_dict()
            self.splits = self.yf_stonk.splits.to_dict()
            self.earnings = self.yf_stonk.earnings.to_dict()
            self.company_data = {column: self.yf_stonk.info[column] for column in company_columns}
            self.current_stock = {column: self.yf_stonk.info[column] for column in current_stock_columns}
            self.historical_stock = {column: self.yf_stonk.info[column] for column in historical_stock_columns}
            self.financials = {column: self.yf_stonk.info[column] for column in financials_columns}
            self.holders = {column: self.yf_stonk.info[column] for column in holders_columns}
            self.logo = {column: self.yf_stonk.info[column] for column in logo_columns}
        except KeyError:
            pass

    def __eq__(self, other):
        return self.name == other.name

    def price_history(self) -> dict:
        dec_place = 2
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime.now()
        data = self.yf_stonk.get_history(start=start, end=end)
        data = fix_dataframe(data)

        open_price = [round(item, dec_place) for item in data['Open'].to_list()]
        close = [round(item, dec_place) for item in data['Close'].to_list()]
        high = [round(item, dec_place) for item in data['High'].to_list()]
        low = [round(item, dec_place) for item in data['Low'].to_list()]
        volume = [round(item, dec_place) for item in data['Volume'].to_list()]
        diff = [round(cl - op, dec_place) for op, cl in list(zip(open_price, close))]
        high_low_diff = [round(high - low, dec_place) for high, low in list(zip(high, low))]
        date_range = [item.strftime('%d %b %Y') for item in data['Date']]

        return {
            "name": self.name,
            "open": open_price,
            "close": close,
            "high": high,
            "low": low,
            "volume": volume,
            "diff": diff,
            "high_low_diff": high_low_diff,
            "date_range": date_range,
        }

    def parse_latest_recs(self):
        return dict(
            self.yf_stonk.recommendations.sort_values(
                ['Firm', 'Date']
            ).drop_duplicates(
                'Firm', keep='last'
            ).groupby('To Grade').count().to_dict()['Action']
        )


class MarketTicker(Stonk):
    def __init__(self, stonk: str):
        super().__init__(stonk)
