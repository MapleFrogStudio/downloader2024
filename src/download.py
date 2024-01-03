# BACKUP UNTIL 500 tickers download enabled
import sys
import json
import datetime
import yfinance as yf
from src import github


class DownloadManager:
    def __init__(self, exchange='tsx'):
        self.exchange = exchange
        self.source_file_name = f'{exchange}.csv'
        self.source = []
        self.cleaned_symbols = []
        self.bad = []
        self.prices_df = None
        self.bad_filename = f'DATA/{self.exchange}_bad_symbols.json'

    def load_source_symbols_from_github(self):
        g = github.Github()
        self.source = g.grab_symbols_list(filename=self.source_file_name)

    def load_bad_tickers_from_local_filesystem(self):
        try:
            # Open the JSON file and load the data
            with open(self.bad_filename, 'r') as json_file:
                data = json.load(json_file)
                
                # Check if the 'bad_symbols' key is present in the loaded data
                if 'bad_symbols' in data:
                    self.bad = data['bad_symbols']
                else:
                    # Add you error handling here, we keep going
                    self.bad = []
        except FileNotFoundError:
            # Add you error handling here, we keep going
            self.bad = []
        except json.JSONDecodeError:
            # Add you error handling here, we keep going
            self.bad = []

    def remove_bad_tickers_from_source(self):
        cleaned_source = [symbol for symbol in self.source if symbol not in self.bad]
        self.cleaned_symbols = cleaned_source

    def download_yahoo_minute_prices(self):
        if not isinstance(self.source,list):
            return None
        if len(self.source) <= 1:
            return None
        
        data = yf.download(self.cleaned_symbols, period='1d', interval="1m", ignore_tz = True, prepost=False)
        
        data = data.loc[(slice(None)),(slice(None),slice(None))].copy()
        data = data.stack()
        data = data.reset_index()
        data.rename(columns={'level_1': 'Symbol'}, inplace=True)
        data.rename(columns={'level_0': 'Datetime'}, inplace=True)
        data.set_index('Datetime', inplace=True)
        self.prices_df = data

    def minute_prices_to_csv(self):
        date_obj = datetime.datetime.now()
        self.prices_df.to_csv(f'DATA/{self.exchange}-{date_obj.date()}.csv', index=True)

    def find_bad_symbols_from_downloaded_data(self):
        unique_symbols = self.prices_df['Symbol'].unique().tolist()
        self.bad = [symbol for symbol in self.source if symbol not in unique_symbols]


    def save_bad_tickers_to_local_filesystem(self):
        data = {'bad_symbols': self.bad}
        with open(self.bad_filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)        

def main(exchange='tsx'):
    print(f'**************** {exchange} ***********************')
    d_handler = DownloadManager(exchange)
    d_handler.load_source_symbols_from_github()
    d_handler.load_bad_tickers_from_local_filesystem()
    d_handler.remove_bad_tickers_from_source()
    d_handler.download_yahoo_minute_prices()
    d_handler.minute_prices_to_csv()
    d_handler.find_bad_symbols_from_downloaded_data()
    d_handler.save_bad_tickers_to_local_filesystem()

def download_one_symbol(symbol):
    data_df = yf.download(symbol, period='1d', interval="1m", ignore_tz = True, prepost=False)
    data_df.to_csv(f'{symbol}.csv', index=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        download_one_symbol(sys.argv[1])
    else:
        main()
    
