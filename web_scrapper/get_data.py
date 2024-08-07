
from web_scrapper.values import *
from web_scrapper.logger import logger

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import pandas as pd
import json
from io import StringIO


class nse_data:
    def __init__(self, path):
        self.session = None  # Session object
        self.path = path    # Initialise the path for files
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
        url = self.path + f"\{name}.csv"
        data = pd.DataFrame(data)
        data.to_csv(url, sep=",")
        print("Data saved in file : {}".format(url))
        logger.info("Data stored in file : {}".format(url))

    def get_url_data(self, relative_url:str, domain:str = None, cookies:dict = None) -> str|None:
        '''
        Send request to the Relative url and returns the extracted html response

        :param relative_url: The relative url for the nse website
        :param domain: (Optional) Domain you want to connect to 
        :param cookies: (Optional) Cookies value for the website
        '''
        domain = self.BASE_URL if not domain else domain
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        url = urljoin( domain , relative_url)
        self.initial_session(domain)
        search_results = None

        print("Sending request to website : {}".format(url) )
        logger.info("Sending reques to url : {}".format(url))

        try:
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

    def get_all_indices(self, indice_type:list = url_data.major_indices.value, save_data:bool = False) -> dict|None :
        '''
        Returns all the nifty indices name and links from one of the categories mentioned in url_data.major_indices

        :param indice_type: (Optional) One of the values from url_data.major_indices.value otherwise gives all indices
        :param save_data : (Optional) To save the data in a csv file
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
                return None

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

    def get_stocks_list(self, indice_url:str, save_data = False) -> dict|None :
        '''
        Get all the stocks present in the given indice url (which can be gathered from get_all_indices)

        :param indice_relative_url : Url to get the stocks data list from
        :param save_data : (Optional) Boolean value to save data as a csv file
        '''
        link_domain = urlparse(indice_url).netloc
        url_data = self.get_url_data(indice_url, link_domain)
        if not url_data:
            return None

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
                logger.info("Extracting csv data from : ",link)
                response = requests.get(link, headers=self.headers)
                print("--- CSV file downloaded ---")

                if response.status_code == 200:
                    data = StringIO(response.text)
                    df = pd.read_csv(data)
                    print(f"\nTotal Stocks : {len(df)}\nColumns : {df.columns.to_list()}")
                    if save_data:
                        self.save_data(df, indice_name)
                    return df.to_dict(orient='list')
                else:
                    print("Failed to download the CSV file. Status code:", response.status_code)
                    logger.error("Failed to download csv file : (response code) ",response.status_code)

    def stock_data(self,symbol:str, return_raw:bool = False) -> dict|None :
        '''
        Extracts data for the stock in real time for the current day 
        Adviced to not use when the market is currently open

        :param symbol: The stock identification symbol in NSE
        :param return_raw: (Optional) returns the entire json fromt he request
        '''
        url = url_data.stock_data_api.value.format(symbol.upper().strip())
        response = self.get_url_data(url)
        
        print("Extracting information for the stock : {}".format(symbol))
        logger.info("Extracting information for the stock : {}".format(symbol))

        if response:
            response = json.loads(response)
            if return_raw: return response
            else:
                pass
            
        return None



