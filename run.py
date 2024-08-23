
from web_scrapper.get_data import nse_data
from web_scrapper.values import *
import os
import pandas as pd

current_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_folder)

a = nse_data(current_folder)

# print(a.get_stocks_list("https://www.nseindia.com/products-services/indices-niftynext50-index"))
print(a.stock_data("RELIANCE",True))
# print(a.historical_stock_data("RELIANCE"))


# Market cap --- for stocks
