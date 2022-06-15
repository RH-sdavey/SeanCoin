company_columns = [
    'sector',
    'fullTimeEmployees',
    'longBusinessSummary',
    'website',
    'industry',
    'currency',
    'exchangeTimezoneName'
]
current_stock_columns = [
    'currentPrice',
    'previousClose',
    'open',
    'dayLow',
    'dayHigh',
    'volume',
    'floatShares',
    'sharesOutstanding',
    'sharesShort',
    'shortRatio'
]
historical_stock_columns = [
    'fiftyDayAverage',
    'twoHundredDayAverage',
    'fiftyTwoWeekHigh',
    'fiftyTwoWeekLow',
    'averageVolume10days',
    'impliedSharesOutstanding'
]
financials_columns = [
    'marketCap',
    'totalCash',
    'totalDebt',
    'totalCashPerShare',
    'totalRevenue',
    'revenuePerShare',
    'grossProfits',
    'forwardPE',
    'profitMargins',
    'revenueGrowth',
    'operatingMargins',
    'freeCashflow',
    'debtToEquity'
]
dividend_split_columns = [
    'lastDividendValue',
    'lastSplitFactor'
]
holders_columns = [
    'heldPercentInstitutions',
    'heldPercentInsiders'
]
logo_columns = [
    'logo_url'
]
all_crypto = {
    "eth": "ETH-USD",
    "btc": 'BTC-USD',
    "lrc": 'LRC-USD',
    "doge": 'DOGE-USD',
    "shib": 'SHIB-USD',
}

all_stonk = ["GME", "AMC", "BB", "KOSS", "BBBY", "TSLA"]


stonk_object = None
