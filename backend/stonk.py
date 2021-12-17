import datetime as dt
import yfinance_ez as yf

from backend.lib import (
    company_columns, current_stock_columns, historical_stock_columns,
    financials_columns, dividend_split_columns, holders_columns, logo_columns
)


class Stonk:
    def __init__(self, stonk: str):
        self.name = stonk
        self.yf_stonk = yf.Ticker(self.name)
        self.hist = self.yf_stonk.get_history(period=yf.TimePeriods.FiveYears)
        self.price_history = self.price_history()
        self.financial_data = self.get_financial_data()
        self.dividends = self.yf_stonk.dividends.to_dict()
        self.splits = self.yf_stonk.splits.to_dict()
        self.earnings = self.yf_stonk.earnings.to_dict()
        self.balance_sheet = self.yf_stonk.balance_sheet
        self.company_data = {column: self.yf_stonk.info[column] for column in company_columns}
        self.current_stock = {column: self.yf_stonk.info[column] for column in current_stock_columns}
        self.historical_stock = {column: self.yf_stonk.info[column] for column in historical_stock_columns}
        self.financials = {column: self.yf_stonk.info[column] for column in financials_columns}
        self.div_split = {column: self.yf_stonk.info[column] for column in dividend_split_columns}
        self.holders = {column: self.yf_stonk.info[column] for column in holders_columns}
        self.logo = {column: self.yf_stonk.info[column] for column in logo_columns}

    def __eq__(self, other):
        return self.name == other.name

    def get_financial_data(self):
        return {
            "q_dates": [item['date'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['quarterly']],
            "q_rev": [item['revenue'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['quarterly']],
            "q_earn": [item['earnings'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['quarterly']],
            "y_dates": [item['date'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['yearly']],
            "y_rev": [item['revenue'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['yearly']],
            "y_earn": [item['earnings'] for item in self.yf_stonk.financials_data['earnings']['financialsChart']['yearly']],
            "q_est_earn": [item['estimate'] for item in self.yf_stonk.financials_data['earnings']['earningsChart']['quarterly']],
            "q_actual_earn": [item['actual'] for item in self.yf_stonk.financials_data['earnings']['earningsChart']['quarterly']],
            "q_date_earn": [item['date'] for item in self.yf_stonk.financials_data['earnings']['earningsChart']['quarterly']],
        }

    def price_history(self) -> dict:
        dec_place = 2
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime.now()
        data = self.yf_stonk.get_history(start=start, end=end)
        data = data.reset_index(level=[0])

        open_price = [round(item, dec_place) for item in data['Open'].to_list()]
        close = [round(item, dec_place) for item in data['Close'].to_list()]
        # high = [round(item, dec_place) for item in data['High'].to_list()]
        # low = [round(item, dec_place) for item in data['Low'].to_list()]
        volume = [round(item, dec_place) for item in data['Volume'].to_list()]
        diff = [round(cl - op, dec_place) for op, cl in list(zip(open_price, close))]
        date_range = [item.strftime('%d %b %Y') for item in data['Date']]

        return {
            "name": self.name,
            "open": open_price,
            "close": close,
            # "high": high,
            # "low": low,
            "volume": volume,
            "diff": diff,
            "date_range": date_range,

        }
