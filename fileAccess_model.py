import pandas as pd
from datetime import datetime
import os

""" Put all file i/o functions in here"""
class FileAccess_model:
    def _openXLSL(self,filepath):
        """ Open an excel spreadsheet file with pandas
            filepath:str - path to the excel file that is to be opened
            -> list of rows where each row is a list of column values
            """  
        df = pd.read_excel(filepath)
        rows = list()
        #columns of data we want are labeled 'RSS Supplier Reel ID', 'Batch width', 'Unrestricted Own Stock(KG)', 'Material'  
        #column_indexes = df.columns.get_indexer(['RSS Supplier Reel ID', 'Batch width', 'Unrestricted Own Stock(KG)', 'Material'])
        column_indexes = df.columns.get_indexer(['Batch', 'Batch width', 'Unrestricted Own Stock(KG)', 'Material'])

        for row in df.itertuples(index=False):
            if not pd.isna(row[column_indexes[0]]): # ignore rows that have no value for the barcode.(empty cells return a float NaN)
                #print(f'barcode is {row[column_indexes[0]]}')
                #print(f'row[column_indexes[1] = {row[column_indexes[1]]}')
                rows.append([str(row[column_indexes[0]]),int(row[column_indexes[1]]),int(row[column_indexes[2]]),str(row[column_indexes[3]])])
        return rows

    def get_rows(self,filepath):
        """ Get records from an excel spreadsheet
            returns a list of row data where each row data is a list of column values"""
        rows = self._openXLSL(filepath)
        return rows
    
    def save_progress(self,filepath,json_records)->None:
        """ Save the jsong string to the file specified in filepath"""
        with open(filepath,"w") as f:
            f.write(json_records)
            
    def load_progress(self,filepath:str)->str:
        with open(filepath,"r") as f:
            json_string = f.read()
        return json_string

    def log_scanned_barcode(self, barcode: str):
        """Append a barcode to a daily log file for emergency recovery."""
        # e.g. logs/2025-09-21.txt
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        filename = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d") + ".txt")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(barcode + "\n")