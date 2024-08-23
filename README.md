# NSE-web-scrapper
Creating a web scrapper powered by `Requests` and `Beautiful Soup` to extract data from NSE Website related to stocks and Indices

## Table of Content
1. [Package Structure](#package-structure)
2. [Features](#features)
3. [How to Use](#how-to-use)
4. [Database Structure](#database-structure)
5. [Contact](#contact)

## Package Structure
```bash
  ├── src/
  |    ├── __init__.py
  |    ├── get_data.py
  |    ├──  logger.py
  |    └── values.py
  ├── requirements.txt
  ├── run.py
  ├── config.py
  ├── database.py
  ├── tables.sql
  ├── queries.sql
  └── README.md
```
## Features
* **URL Management** : It utilises requests to initialise sessions and get data from the preloaded url's in `values.py`
* **Data Extraction** : HTML parser using Beautiful Socp
* **Data Storage** : Extracted data can be stored in the form of a `.csv` file and collected in the form of `dict` 
* **Biltin Logger** :  for logging all the details in 3 levels (info, warning, error) in the `log.log` file

Check the `run.py` file for some dummy codes and examples of now to use and store the data gathered from the scrapper in a database

## How to Use

Import the package
```bash
from web_scrapper.get_data import nse_data
from web_scrapper.values import *
```
Initialise an object for the `nse_data class`
<br>Along with required argument `path` for initialising the storage location for files
```bash
import os
current_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_folder)

objectName = nse_data(current_folder) 
```
Use the required functions with the object
```bash
objectName.stock_data("RELIANCE",True)  # Get information about a particular stock
objectName.historical_stock_data("RELIANCE")   # Historical data for stock prices
objectName.get_all_indices(save_data=True)   # Get all the indices list along with the url
```

## Database Structure

The SQL query to create the tables can be seen in `tables.sql` file
<br>Some mock queries that can be useful are also given in `queries.sql` file

![Test Image 5](/database_schema.png)

## Contact 

For any questions or feedback, please contact at `mananagarwal1784@gmail.com` <br>
Visit my [Website](https://manan-portfolio.ddns.net/) to check out my works




