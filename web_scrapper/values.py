from enum import Enum

class url_data(Enum):
    indice_url = "/products-services/indices-"
    search_url = '/api/search/autocomplete?q={}'    
    stock_data_url = "/get-quotes/equity?symbol={}"
    stock_data_api = "/api/quote-equity?symbol={}"
    stock_historical_data = "api/historical/cm/equity?symbol={}"
    major_indices = ["Broad Market","Sectoral","Thematic"]
    # niftyindices.com
    indice_stock = "/market-data/equity-stock-watch?Iname={}"

class stock_data_id(Enum):
    stock_data_id = {
        "current_price":"quoteLtp",
        "traded_volume_lakhs": "orderBookTradeVol",
        "traded_value_cr":"orderBookTradeVal",
        "total_market_cap_cr:":"orderBookTradeTMC",
        "52_week_high_date":"week52HighDate",
        "52_week_high_value":"week52highVal",
        "52_week_low_date":"week52HighDate",
        "52_week_low_value":"week52highVal",
    }
    securities_info = {
        "Date_of_Listing" : "date_of_listing" ,
        "SectoralIndxPE" : "adjusted_p_e",
        "Symbol_PE" : "symbol_p_e"
    }
