# ml_project_2020
Using the Ethereum graph to predict prices of Ethereum tokens

## Obtaining transaction data

```
python3 ethplorer_scraper.py erc20_contracts_with_max_page.csv
```
For different versions of OS appropriate path to chromedriver should be placed in ethplorer_scraper.py line 23.
This script will walk in a cycle over tokens that are in a CSV file and scrab pages one by one. For each token automatically will be created a directory in outputs/token_name_timestamp. In this directory will be saved CSV files of parsed data such as transaction timestamp,  from address, to address.

After that simple script could be used to delete recurring rows and make one CSV. See the result in data directory (some files had to be compressed). On a decent computer, it's iterate approximately 1 page with 100 rows per 3 seconds. Siumolteniuosly only one or two copies of this program could be launched.
The preprocessed result should be moved to "data" directory.
##Graph embeddings
To launch graph embedding preprocessing launch 
```
python3 csv_preprocessing.py
```
This script will take for input the results from "data" directory and build graph embeddings for them.
The results of graph embeddings will be saved in the preprocessed directory.

For small files, it takes about 10 seconds per row for iteration, so for processing the smallest data/ftt.csv, it will take about one hour. For tokens with a larger number of iterations, it will take up to a few hours or days. The main bottleneck of this code is using a list and dictionary python data structure in such a big dataset and some nonoptimal loops. For the quick prototype purposes, we didn't look too deep into optimizing this code with more suitable data structures such as set, deque, NumPy array. 

## Baseline Model Description:

Inside the Baseline Models folder, we find 12 new folders, each one with the files used for the analysis of each token. Within each of these folders, we find the dataset, the code, and the images obtained from the visual analysis and forecasting. The code contains the processing of the dataset, a visual analysis of the time series, and the implementation of each of the three methods (ARIMA, SES_Tetha, and HWES) with validation and forecasting of 10 timesteps. The code is fully reproducible, so you just need to run all in order to obtain the results.



## Obtaining price data

1) Scraping sheet top500 tokens with eidoo
2) Using ccxt tool to interact with all exchanges, 
2.1) Registration on all exchanges (the list is in the laptop), downloading the keys api (you may have already downloaded my keys to the Github, if so, I will deactivate them all), search for trading pairs for an existing sheet of 500 tokens.
3) Search for exchanges with data for two years 
4) All that's left is binance 
5) Discharge of 95 tokens from the binansa from 01.01.2018 at the hour level