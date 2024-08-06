from bs4 import BeautifulSoup
from urllib import request
from urllib.parse import urlparse, urljoin
import requests
import pandas as pd
from io import StringIO
import os
import logging

current_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_folder)

def create_logger():
    '''
    Creating and initializing the logger
    Log file : Logs.log
    log Levels : info / warning / error
    '''

    # Logger.info/warning/error
    # logger = create_logger()
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logs.log',  
        level=logging.DEBUG,
        encoding='utf-8', 
        filemode='w',
        format='[%(asctime)s] | %(levelname)s | %(funcName)s >>> %(message)s',
        datefmt="%B %d, %H:%M:%S",)

    logger.info("Logger configured...")
    return logger

class nse_data:

    def __init__(self, path):
        self.BASE_URL = "https://www.nseindia.com"  # Base url of the nse website
        self.head = {"user-agent": "Chrome/87.0.4280.88"}  # Web Browser for the session
        self.urls = {  # Basic important relative urls
            "indices":"/products-services/about-indices",
            "stock_data" : "/get-quotes/equity?symbol={}"
        }
        self.major_indices = ["Broad Market","Sectoral","Thematic"]  # Import indices
        self.session = None  # Session object
        self.path = path
        self.stock_data_ids = {
            "current_price":"quoteLtp",
            "traded_volume_lakhs": "orderBookTradeVol",
            "traded_value_cr":"orderBookTradeVal",
            "total_market_cap_cr:":"orderBookTradeTMC",
            "52_week_high_date":"week52HighDate",
            "52_week_high_value":"week52highVal",
            "52_week_low_date":"week52HighDate",
            "52_week_low_value":"week52highVal",
        }
        self.securities_info = {
                "Date_of_Listing" : "date_of_listing" ,
                "SectoralIndxPE" : "adjusted_p_e",
                "Symbol_PE" : "symbol_p_e"
            }
        print("\n Object Initialized")
    
    # Initializing the Session for the website
    def initial_session(self, domain = None) -> None:
        self.session = requests.session()
        if not domain :
            self.session.get( self.BASE_URL,headers=self.head)
        else:
            self.session.get( domain, headers = self.head)
        print("Session Initialized")

    # Saves the given Dataframe as a csv file in the specified path
    def save_data(self,data:dict, name:str) -> None:
        '''
        data : Dataframe containing the data to store
        name : Name of the csv file
        '''
        url = self.path + f"\{name}.csv"
        print("Data Stored into file : ", url)
        data.to_csv(f"{self.path}/{name}.csv", sep=",")

    # Returning the entire source code for the give Relative Url
    def get_url_data(self, url:str, cookies = None) -> str|None:
        '''
        url : The relative url for the nse website
        cookies : Cookies value for the website
        '''
        url = urljoin(self.BASE_URL,url)
        print("\nExtracting URL data .....\nAbsolute Url : ", url)
        search_results = None
        self.initial_session()  

        try:
            if not cookies:
                response = self.session.get(url, headers=self.head)
            else:
                response = self.session.get(url, headers=self.head, cookies = cookies)
            if response.status_code == 200:
                return response.text
            else:
                print("Url does not exists, Status Code : ", response.status_code)
                return None

        except requests.exceptions.RequestException as e:
            print("Requesting Url Exception : ", e)
            return None

    # Returning all the indices link on the given Major Indice
    def get_indices(self, indice_type, save_data = False) -> pd.DataFrame|None :
        '''
        indice_type : One of the values from self.major_indices
        save_data : Saving the data as a csv file
        '''

        url = "/products-services/indices-" + "-".join(indice_type.lower().split())
        url = urljoin(self.BASE_URL, url)
        data_collected = {"name":[],"links":[]}
        outside_links = {"name":[],"links":[]}

        url_data = self.get_url_data(url)
        if not url_data:
            return None
        soup = BeautifulSoup(url_data,"html.parser")
        ul = soup.find(class_="mt-3").find("ul")

        for tag in ul.find_all("a"):
            absolute_link = urljoin(self.BASE_URL, tag.get("href"))
            link_domain = urlparse(absolute_link).netloc
            if link_domain ==urlparse(self.BASE_URL).netloc:
                data_collected["name"].append(tag.text.strip())
                data_collected["links"].append(urlparse(absolute_link).path)
            else:
                outside_links["name"].append(tag.text.strip())
                outside_links["links"].append(tag.get("href"))

        df = pd.DataFrame(data_collected)
        print(f"\n---- Stats of the Collected Indices ---- \nTotal values collected : {len(df)} \nTotal Outside Links : {len(outside_links['name'])}\n")
        if save_data:
            self.save_data(df, indice_type)
        return df, pd.DataFrame(outside_links)

    # Returning the list of stocks listed inside a Indice
    def get_indices_stocks_list(self, indice_relative_url:str, save_data = False) -> pd.DataFrame|None :
        '''
        indice_relative_url : Relative url for the index
                            /products-services/indices-<indice_name>
        save_data : Boolean value to save data as a csv file
        '''

        url = urljoin(self.BASE_URL, indice_relative_url)
        url_data = self.get_url_data(url)
        if not url_data:
            return None

        soup = BeautifulSoup(url_data,"html.parser")
        indice_name = soup.find(class_="section-heading").text.strip()
        links = soup.find(class_="mt-3").find_all('a')
        print("\nIndice Name : ",indice_name,"\nTotal Links Extracted : ", len(links))

        for link in links:
            link = link.get("href")
            if link.lower().endswith('csv'):
                print("\nExtracting the CSV File....\nUrl : ",link)
                response = requests.get(link, headers=self.head)
                print("--- CSV file downloaded ---")

                if response.status_code == 200:
                    data = StringIO(response.text)
                    df = pd.read_csv(data)
                    print(f"\nTotal Stocks : {len(df)}\nColumns : {df.columns.to_list()}")
                    if save_data:
                        self.save_data(df, indice_name)
                else:
                    print("Failed to download the CSV file. Status code:", response.status_code)
                               
a = nse_data(current_folder)
