import time
import sys
import json
import datetime
import yfinance as yf
from src import github


class DownloadManager:
    def __init__(self, group='tsx1'):
        self.group = group
        self.source_file_name = f'{group}.csv'
        self.source = []
        self.prices_df = None

    def load_source_symbols_from_github(self):
        g = github.Github()
        self.source = g.grab_symbols_list(filename=self.source_file_name)

    def download_yahoo_minute_prices(self):
        if not isinstance(self.source,list):
            return None
        if len(self.source) <= 1:
            return None
        
        data = yf.download(self.source, period='1d', interval="1m", ignore_tz = True, prepost=False)
        
        data = data.loc[(slice(None)),(slice(None),slice(None))].copy()
        data = data.stack()
        data = data.reset_index()
        data.rename(columns={'level_1': 'Symbol'}, inplace=True)
        data.rename(columns={'level_0': 'Datetime'}, inplace=True)
        data.set_index('Datetime', inplace=True)
        self.prices_df = data

    def minute_prices_to_csv(self):
        date_obj = datetime.datetime.now()
        self.prices_df.to_csv(f'DATA/{self.group}-{date_obj.date()}.csv', index=True)


def main(group='tsx1'):
    print(f'**************** {group} ***********************')
    d_handler = DownloadManager(group)
    d_handler.load_source_symbols_from_github()
    d_handler.download_yahoo_minute_prices()
    d_handler.minute_prices_to_csv()

def download_one_symbol(symbol):
    data_df = yf.download(symbol, period='1d', interval="1m", ignore_tz = True, prepost=False)
    data_df.to_csv(f'{symbol}.csv', index=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        download_one_symbol(sys.argv[1])
    else:
        main()   
    