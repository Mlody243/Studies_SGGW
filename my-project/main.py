import requests as rq
import os
import csv
from datetime import datetime

def dekorator(func):
    def wrapper(*args,**kwargs):
        print(f'Uruchomiono program o godzinie: {datetime.now():%Y-%m-%d %H:%M:%S}')
        wynik=func(*args,**kwargs)
        print(f'Zakończono program o godzinie: {datetime.now():%Y-%m-%d %H:%M:%S}')
        return wynik
    return wrapper
class NetworkErrors(Exception):
    """
    Here you can define how to handle Errors
    """
    pass
class AccessDeniedError(NetworkErrors):
    """
    403 errors are handled here
    """
    def __init__(self, url, error_code='Access Forbidden (403)'):
        self.url=url
        self.message=f'{error_code} url {url}'
        super().__init__(self.message)    
class NotFoundError(NetworkErrors):
    """
    404 errors are handled here
    """
    def __init__(self, url, error_code='Not found (404)'):
        self.message=f'{error_code} url {url}'
        super().__init__(self.message)


class ETL_simple:
    def  __init__(self,input_path='latest.txt',values_file='values.csv',missing_file='missing_values.csv'):
        self.input_path=input_path
        self.values_file=values_file
        self.missing_file=missing_file
    def extract(self):
        with open(self.input_path,newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f,fieldnames = ['ID', 'Val1', 'Val2', 'Val3', 'Val4', 'Val5', 'Val6', 'Val7'])
            for row in reader:
                yield row
    def transform(self,line_data):
        for row in line_data:
            row_id = row.get('ID')
            missing_keys = [key for key, val in row.items() if key != 'ID' and val.strip() == '-']
            numeric_values = []
            for key, val in row.items():
                if key != 'ID':
                    val_cleaned = val.strip()
                    if val_cleaned != '-' and val_cleaned:
                        try:
                            numeric_values.append(float(val_cleaned))
                        except ValueError:
                            pass
            total_sum = sum(numeric_values) if numeric_values else 0.0
            average = (total_sum / len(numeric_values)) if len(numeric_values) > 0 else 0.0
            yield {
                "row_number": row_id,
                "sum": total_sum,
                "average": average,
                "missing_indices": missing_keys,
            }

    def load(self,values_dict):
         with open(
            self.values_file, "w", newline="", encoding="utf-8"
        ) as values_file, open(
            self.missing_file, "w", newline="", encoding="utf-8"
        ) as missing_file:

            values_writer = csv.writer(values_file)
            missing_writer = csv.writer(missing_file)

            # Nagłówki plików
            values_writer.writerow([
                "numer_porządkowy", "suma", "średnia"
            ])
            missing_writer.writerow([
                "numer_porządkowy", "indeksy_brakujących_kolumn"
            ])
            for record in values_dict:
                # Zapis sumy i średniej
                values_writer.writerow([
                    record["row_number"],
                    record["sum"],
                    record["average"]
                ])
                if len(record['missing_indices'])>0:
                    missing_writer.writerow([
                        record["row_number"],
                        record['missing_indices']
                    ])
    @dekorator
    def run(self):
        self.load(self.transform(self.extract()))

def download_file_from_url(url:str,save_name:str='latest.txt'):
    response=rq.get(url)
    if response.status_code==403:
        raise AccessDeniedError(url)
    elif response.status_code==404:
        raise NotFoundError(url)
    else:
        response.raise_for_status()
        with open(save_name,'wb') as f:
            f.write(response.content)
        print('succesfully downloaded file from URL',url,'and saved as',save_name, 'in path',os.getcwd())

if __name__=='__main__':
    # download_file_from_url('https://oleksandr-fedoruk.com/sggw/podyplomowe/403','latest_3.txt')
    # download_file_from_url('https://oleksandr-fedoruk.com/sggw/podyplomowe/404','latest_4.txt')
    ex_1=ETL_simple('latest.txt','values.csv','missing_values.csv')
    ex_1.run()