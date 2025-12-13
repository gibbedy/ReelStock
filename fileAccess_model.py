import pandas as pd
from datetime import datetime
import os, sys
from pathlib import Path
import shutil

""" Put all file i/o functions in here"""


def app_dir() -> Path:
    """Folder of the running EXE when frozen, else the .py file’s folder.
        This enables a filepath to be setup in the working directory when run
        from python and a pyinstaller exe."""
    if getattr(sys, "frozen", False):          # PyInstaller (onefile or onedir)
        return Path(sys.executable).parent     # e.g. .../dist/ReelStock
    return Path(__file__).resolve().parent     # source run

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def resource_path(rel):
    """gets correct filepath for assets weather we used pyinstaller onefile or ondfolder"""
    base = getattr(sys, "_MEIPASS", None) or (
        os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(base, rel)


class FileAccess_model:
    SAVE_DIR = "save_files"
    LOG_DIR = "logs"
    ARCHIVE_DIR = "archive"
    
    full_path_save_dir = ensure_dir(app_dir() / SAVE_DIR)
    full_path_log_dir = ensure_dir(app_dir() / LOG_DIR)
    full_path_archive_dir = ensure_dir(app_dir() / ARCHIVE_DIR)

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
                rows.append([str(row[column_indexes[0]]),int(row[column_indexes[1]]),int(row[column_indexes[2]]),str(row[column_indexes[3]])])
        return rows

    def get_rows(self,filepath):
        """ Get records from an excel spreadsheet
            returns a list of row data where each row data is a list of column values"""
        rows = self._openXLSL(filepath)
        return rows
    
    def save_progress(self,filepath,json_records)->None:
        """ Save the jsong string to the file specified in filepath"""
        save_path = self.full_path_save_dir / filepath
        with open(save_path,"w") as f:
            f.write(json_records)
            
    def load_progress(self,filepath:str)->str:
        with open(filepath,"r") as f:
            json_string = f.read()
        return json_string

    def log_scanned_barcode(self, barcode: str):
        """Append a barcode to a daily log file for emergency recovery."""
        # e.g. logs/2025-09-21.txt
        filename = self.full_path_log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.txt'
        with open(filename, "a", encoding="utf-8") as f:
            f.write(barcode + "\n")
    
    def get_latest_save_path(self) -> str:
        """Return the newest save file path from ./save_files, or '' if none."""
        folder = self.full_path_save_dir
        if not folder.exists():
            return ""
        files = list(folder.glob("save_file_*"))
        if not files:
            return ""
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    def delete_file(self,filepath):
        os.remove(filepath)

    def get_old_save_paths(self,num_of_files_to_keep:int)->list[str]:
        """get a list of files paths excluding the num_of_files_to_keep number of most recently modified files"""
        folder = self.full_path_save_dir
        if not folder.exists():
            return ""
        files = list(folder.glob("save_file_*"))
        if not files:
            return ""
        files.sort(key=lambda p: p.stat().st_mtime)
        files = [str(f) for f in files[:-3]]
        return files
    
    def cleanup_save_files(self):
        """Delete all but a reasonable number of save files"""
        ...
    def copy_file(self,source:str, dest:str):
        if source and dest:
            shutil.copy2(src=source,dst=dest)

    def delete_save_files(self):
        """delete all save files"""
        folder = self.full_path_save_dir
        files = list(folder.glob("save_file_*"))
        for file in files:
            self.delete_file(file)

    def archive_tests(self):
        """ Move the latest save file to the archive directory and delete the rest"""
        file_to_archive:str = self.get_latest_save_path()
        file_from = file_to_archive
        dir_to = self.full_path_archive_dir
        print(f"source: {file_from} dest: {dir_to}")
        self.copy_file(source = file_from, dest=dir_to)
        self.delete_save_files()
        

