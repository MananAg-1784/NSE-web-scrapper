# NSE-web-scrapper
Creating a web scrapper powered by `Requests` and `Beautiful Soup` to extract data from NSE Website related to stocks and Indices
* It utilises requests to initialise sessions and get data from the presented url
* HTML is parsed using BeautifulSoup
* Extracted data can be stored in the form of a `.csv` file and collected in the form of `dict`
* Builtin Logger for logging all the details in 3 levels (info, warning, error)

Check the `run.py` file for some dummy codes and examples of now to use and store the data gathered from the scrapper in a database

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
  └── README.md
```

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

## Contact 

For any questions or feedback, please contact at `mananagarwal1784@gmail.com` <br>
Visit my [Website](https://manan-portfolio.ddns.net/) to check out my works




