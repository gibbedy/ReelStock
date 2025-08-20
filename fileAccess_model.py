import pandas as pd

""" Put all file i/o functions in here"""
class FileAccess_model:
    def _openXLSL(self,filepath):
        """ Open an excel spreadsheet file with pandas
            filepath:str - path to the excel file that is to be opened
            -> list of rows where each row is a list of column values
            """  
        df = pd.read_excel(filepath)
        rows = list()
        for row in df.itertuples(index=False):
            if not pd.isna(row._3): # ignore rows that have no value for the barcode.(empty cells return a float NaN)
                rows.append([str(row._3),int(row._2),int(row._7),str(row.Material)])
        return rows

    def get_rows(self,filepath):
        """ Get records from an excel spreadsheet"""
        rows = self._openXLSL(filepath)
        return rows

    