
from web_scrapper.get_data import nse_data
from web_scrapper.values import *
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_folder)

a = nse_data(current_folder)
# a.get_all_indices(save_data=True)
# a.get_stocks_list("https://www.nseindia.com/products-services/indices-nifty50-index",True)
# a.get_stocks_list("https://niftyindices.com/indices/equity/thematic-indices/nifty-ipo",True)
a.stock_data("RELIANCE")