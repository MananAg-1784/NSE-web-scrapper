
from web_scrapper.values import *
from web_scrapper.logger import logger

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import pandas as pd
import json
from io import StringIO
from datetime import datetime, timedelta
from ping3 import ping

class nse_data:
    def __init__(self, path_):
        self.session = None  # Session object
        self.path = path_    # Initialise the path for files
        self.BASE_URL = "https://www.nseindia.com"
        self.INDICE_URL = "https://www.niftyindices.com"
        self.headers ={
        "user-agent": "Chrome/87.0.4280.88"
        }

    def initial_session(self, domain:str = None) -> None:
        '''
        Creates and Initializes the session variable 

        :param domain: (Optional) domain of the website to create the session in
        '''
        try:
            if type(ping("3.6.0.0")) != float:
                raise Exception("Not Connected to the internet")
        except Exception as e:
            print("Ping Error... Check your internet connection and try again...")
            logger.error("Not connected to the internet")
            # raise Exception("Ping Error")
     
        self.session = requests.session()
        if not domain :
            self.session.get( self.BASE_URL, headers = self.headers)
        else:
            self.session.get( domain, headers = self.headers)

        logger.info("Session Initialized >> {}".format(domain))
        print("Session Initialized")

    def save_data(self, data:dict, name:str) -> None:
        '''
        Creates and saves the given pd.DataFrame as a csv file 
        
        :param data: pd.Dataframe containing the data to store
        :param name: Name of the csv file
        '''
        try:
            url = self.path + f"\{name}.csv"
            data = pd.DataFrame(data)
            data.to_csv(url, sep=",")
            print("Data saved in file : {}".format(url))
            logger.info("Data stored in file : {}".format(url))
        except Exception as e:
            print("\nThe file may be available previously\nError saving the file : ",(e))

    def get_url_data(self, relative_url:str, domain:str = None, cookies:dict = None) -> str|None:
        '''
        Send request to the Relative url and returns the extracted html response

        :param relative_url: The relative url for the nse website
        :param domain: (Optional) Domain you want to connect to 
        :param cookies: (Optional) Cookies value for the website

        :return : Returns the HTML response as strings | In case of Exception the function return None
        '''
        domain = self.BASE_URL if not domain else domain
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        url = urljoin( domain , relative_url)
        search_results = None

        print("Sending request to website : {}".format(url) )
        logger.info("Sending reques to url : {}".format(url))

        try:
            self.initial_session(domain)
            if not cookies:
                response = self.session.get(url, headers=self.headers)
            else:
                response = self.session.get(url, headers=self.headers, cookies = cookies)

            if response.status_code == 200:
                print("Response Recieved....")
                logger.info("Response Recieved....")
                return response.text
            else:
                print("Url does not exists, Status Code : ", response.status_code)
                logger.error("Url does not exists, Status Code : {}".format(response.status_code))
                return None

        except requests.exceptions.RequestException as e:
            print("Requesting Url Exception : ", e)
            logger.error("Requesting Url Exception :  {}".format(e))
            return None

    def get_all_indices(self, indice_type:list = url_data.major_indices.value, save_data:bool = False) -> dict :
        '''
        Returns all the nifty indices name and links from one of the categories mentioned in url_data.major_indices

        :param indice_type: (Optional) One of the values from ` url_data.major_indices.value ` otherwise gives all indices
        :param save_data : (Optional) To save the data in a csv file

        :return : Returns the data as dict with [name, links] of the indices
                  In case of any exception or no response returns an empty dict()
        '''
        logger.info("Get indices for : {}".format(indice_type))
        return_response = {}
        count = 0
        for indice in indice_type:
            return_response[indice] = []
            url = url_data.indice_url.value + "-".join(indice.lower().split())
            url = urljoin(self.BASE_URL, url)
            response = self.get_url_data(url)
            if not response:
                return {}

            soup = BeautifulSoup(response,"html.parser")
            ul = soup.find(class_="mt-3").find("ul")

            print("Extracting all the Indices .....")
            for tag in ul.find_all("a"):
                indice_name = tag.text.strip()
                indice_url = urljoin(self.BASE_URL, tag.get("href"))
                return_response[indice].append({"name":indice_name,"url":indice_url})
                count+=1

        print("\n---- Stats of the Collected Indices ---- \nTotal indices collected : {}".format(count))
        logger.info("All Indices successfully extracted")

        if save_data:
            d = {"name":[],"link":[],"indice_type":[]}
            for indice_type in return_response.keys():
                for indices in return_response[indice_type]:
                    d["name"].append(indices["name"])
                    d["link"].append(indices["url"])
                    d["indice_type"].append(indice_type)
            self.save_data(d, "Indices")
        return return_response

    def get_stocks_list(self, indice_url:str, save_data = False) -> list :
        '''
        Get all the stocks present in the given indice url (which can be gathered from get_all_indices)

        :param indice_url : Url to get the stocks data list from
        :param save_data : (Optional) Boolean value to save data as a csv file

        :return : List of dict(Contains data about the individual stocks)
        '''
        link_domain = urlparse(indice_url).netloc
        url_data = self.get_url_data(indice_url, link_domain)
        if not url_data:
            return []

        soup = BeautifulSoup(url_data,"html.parser")
        indice_name = soup.title.text.strip()
        if link_domain == urlparse(self.BASE_URL).netloc:
            link_domain = self.BASE_URL
            indice_name = soup.find(class_="section-heading").text.strip()
        else:
            link_domain = self.INDICE_URL
            indice_name_ = soup.find(id="selectedindexdetail")
            indice_name = indice_name_.text.strip() if indice_name_ else indice_name

        links = soup.find_all('a')
        print("\nIndice Name : ",indice_name,"\nTotal Links Extracted : ", len(links))

        for link in links:
            link = link.get("href")
            if link and link.lower().endswith('csv'):

                link = urljoin(link_domain, link)
                print("\nExtracting the CSV File....\nUrl : ",link)
                logger.info(f"Extracting csv data from : {link}")
                response = requests.get(link, headers=self.headers)
                print("--- CSV file downloaded ---")

                if response.status_code == 200:
                    data = StringIO(response.text)
                    df = pd.read_csv(data)
                    print(f"\nTotal Stocks : {len(df)}\nColumns : {df.columns.to_list()}")
                    if save_data:
                        self.save_data(df, indice_name)
                    return df.to_dict(orient='records')
                else:
                    print("Failed to download the CSV file. Status code:", response.status_code)
                    logger.error("Failed to download csv file : (response code) ",response.status_code)
        return []

    def stock_data(self, symbol:str, return_raw:bool = False) -> dict|None :
        '''
        Extracts data for the stock in real time for the current day 
        Adviced to not use when the market is currently open

        :param symbol: The stock identification symbol in NSE
        :param return_raw: (Optional) returns the entire json fromt he request

        :returns : The dict format for the json data of the stock
        '''
        symbol = symbol.upper()
        url = url_data.stock_data_api.value.format(symbol.upper().strip())
        response = self.get_url_data(url)
        
        print("Extracting information for the stock : {}".format(symbol))
        logger.info("Extracting information for the stock : {}".format(symbol))
        if response:
            response = json.loads(response)
            if return_raw: return response
            else:
                return {key:response[key] for key in ["metadata","priceInfo","industryInfo"]}
        return None

    def historical_stock_data(self, symbol:str, end_date:datetime = datetime.today(), start_date:datetime = None ) -> None|Exception :
        '''
        Extract the 1yr historical data of the stock from the start date
        Returns a csv file that is stored in self.path

        :param symbol: symbol to identify stock
        :param end_date: (Optional) end date for the data extraction (Default: today)
        :param start_date: (Optional) Starting date for the values
        (Deafult: end_date - 1 years)

        :return : Saves the data in an csv file in the path specified during class initialization
                  Exception in any other cases
        '''
        self.initial_session()
        symbol = symbol.upper()
        self.session.get( urljoin(self.BASE_URL,url_data.stock_data_url.value.format(symbol) ) , headers=self.headers)  # to save cookies

        if not start_date:
            start_date = datetime(end_date.year - 1, end_date.month, end_date.day )
        if not start_date < end_date:
            return Exception("The end date is before the starting time period")
        start_date = start_date.strftime("%d-%m-%Y")
        end_date = end_date.strftime("%d-%m-%Y")

        url = url_data.stock_historical_data.value.format(symbol) + "&series=[%22EQ%22]&from=" + start_date + "&to=" + end_date + "&csv=true"
        url = urljoin(self.BASE_URL, url)
        print("Url : ", url)
        logger.info(f"Sending request to url >>>> {url}")

        response = self.session.get(url, headers = self.headers)
        print("Start date : ", start_date, "\nEnd date : ", end_date)
        logger.info("Historical data for {}, From : {}".format(symbol,start_date))

        data = pd.read_csv(StringIO(response.text[3:]))
        self.save_data(data,f"{symbol}_{start_date}")
        
    def search_stocks(self, name:str) -> list :
        '''
        Takes a input string and returns all the possbile equity stocks with the name

        :param name: Input string for the stock name

        :return : List of dict(symbol, comanyName) | Empty list[]
        '''
        name = name.lower()
        url = url_data.search_url.value.format(name)
        response = self.get_url_data(url)
        stocks = []
        if response:
            for i in json.loads(response)["symbols"]:
                stocks.append({"symbol":i["symbol"],"company":i["symbol_info"]})

        print("Stocks with name :", name, "Total : ", len(stocks),"\n")
        return stocks
