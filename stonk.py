from backend.lib import (
    company_columns, current_stock_columns, historical_stock_columns,
    financials_columns, dividend_split_columns, holders_columns, logo_columns
)


class Stonk:
    def __init__(self, stonk: str, **kwargs):
        self.earnings = {}
        self.name = stonk
        try:
            self.__dict__.update(kwargs)
        except TypeError:
            pass
        self.column_names = ['company_columns', 'current_stock_columns', 'historical_stock_columns',
                             'financials_columns', 'dividend_split_columns', 'holders_columns', 'logo_columns']
        self.company_columns = {key: self.__dict__[key] for key in company_columns}
        self.current_stock_columns = {key: self.__dict__[key] for key in current_stock_columns}
        self.historical_stock_columns = {key: self.__dict__[key] for key in historical_stock_columns}
        self.financials_columns = {key: self.__dict__[key] for key in financials_columns}
        self.dividend_split_columns = {key: self.__dict__[key] for key in dividend_split_columns}
        self.holders_columns = {key: self.__dict__[key] for key in holders_columns}
        self.logo_columns = {key: self.__dict__[key] for key in logo_columns}

        self.financial_data = {
            "q_dates": [item['date'] for item in self.earnings['financialsChart']['quarterly']],
            "q_rev": [item['revenue'] for item in self.earnings['financialsChart']['quarterly']],
            "q_earn": [item['earnings'] for item in self.earnings['financialsChart']['quarterly']],
            "y_dates": [item['date'] for item in self.earnings['financialsChart']['yearly']],
            "y_rev": [item['revenue'] for item in self.earnings['financialsChart']['yearly']],
            "y_earn": [item['earnings'] for item in self.earnings['financialsChart']['yearly']],
            "q_est_earn": [item['estimate'] for item in self.earnings['earningsChart']['quarterly']],
            "q_actual_earn": [item['actual'] for item in self.earnings['earningsChart']['quarterly']],
            "q_date_earn": [item['date'] for item in self.earnings['earningsChart']['quarterly']],
        }
