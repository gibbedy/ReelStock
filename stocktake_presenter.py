from __future__ import annotations
from typing import Any,Callable,Protocol
from errors import DuplicateBarcodeError,DatafileNotLoadedError

class View(Protocol):
    """ interface to the view model for gui. That is functions that the view must implement"""
    def create_ui(self,presenter:Stocktake_presenter) -> None:
        ...
    def mainloop() -> None:
        ...
    def get_filepath(self)->str:
        ...
    def create_filepath(self)->str:
        ...
    def display_records(self,rows:list[list[str]])->None:
        ...
    def unknown_reel_found(self,barcode:str):
        ...
    def known_reel_found(self,barcode:str):
        ...
    def display_popup(self,title:str,message:str)->None:
        ...
    def jump_to_barcode(self,barcode:str)->None:
        ...   
    def highlight_barcode(self,barcode:str)->None:
        ...

class File_model(Protocol):
    """ Interface to the file model for file i/o"""
    def get_rows(self)->list[list[str]]:
        ...
    def save_progress(self, filepath:str,json_records:str)->None:
        ...
    def load_progress(self, filepath:str)->None:
        ...

class Records_model(Protocol):
    """ Interface to the records model"""
    def set_records(self,rows:list[list[str]])->None:
        ...
    def get_records(self,hide_found:bool)->list[list[str]]:
        ...
    def barcode_exists(self,barcode:str)->bool:
        ...
    def insert_unknown_reel(self,barcode:str):
        ...
    def mark_as_found(self,barcode:str):
        ...
    def get_test_barcode(self)->str|None:
        ...
    def get_found_barcodes(self)->list[str]|None:
        ...
    def get_unknown_barcodes(self)->list[str]|None:
        ...
    def get_found_unknown_barcodes(self)->list[str]:
        ...
    def get_found_known_barcodes(self)->list[str]:
        ...
    def is_record_known(self,barcode:str)->bool:
        ...
    def is_record_found(self,barcode:str)->bool:
        ...
    def get_report(self)->dict:
        ...
    def to_json_str(self)->str:
        ...
    def load_from_json_str(self,json_str):
        ...

class Scanner_model(Protocol):
    """ Interface to the barcode scanner model"""
    def startScanner(self,presenter:Stocktake_presenter) -> None:
        ...

class Stocktake_presenter:
    def __init__(self,file_model:File_model,records_model:Records_model,view:View,scanner_model:Scanner_model):
        self.file_model = file_model
        self.records_model = records_model
        self.view = view
        self.scanner_model = scanner_model
        self._file_loaded = False 
        self._save_filepath = None
        self.filepath = None
        self.barcodes_already_hidden = list() 
    
    def reset(self)->None:
        """ Reset presenter variables.
            Do this before loading a previously saved stocktake test"""
        self._file_loaded=False
        self._save_filepath = None
        self.filepath = None
        self.barcodes_already_hidden = list()

    def run(self)->None:
        self.view.create_ui(self)
        self.scanner_model.startScanner(self)
        self.view.mainloop()
    
    def _display_records(self,hide_found:bool = False)->None:
        """Fetch all record rows from the records_model and send them to view for displaying."""
        rows = self.records_model.get_records(hide_found=hide_found)
        self.view.display_records(rows)

        found_known_reels = self.records_model.get_found_known_barcodes()
        found_unknown_reels = self.records_model.get_found_unknown_barcodes()

        if hide_found==False:
            for barcode in found_unknown_reels:
                self.view.unknown_reel_found(barcode)
    
            for barcode in found_known_reels:
                self.view.known_reel_found(barcode)

    """functions required by the view"""
    def handle_load_btn(self) -> None:
        self.filepath = self.view.get_filepath()
        try:
            rows = self.file_model.get_rows(self.filepath)
        except FileNotFoundError as e:
            self.view.display_popup(title="Load File", message = "File wasn't found, or you didn't select a file")
            return
        try:
            self.records_model.set_records(rows)
        except  DuplicateBarcodeError as e:
            self.view.display_popup(title="Load File Error", message="The following is a list of reels that were NOT inserted because they have the same ID as a one already loaded:\n " + str(e)) #need to convert set records exeptions to a single string i think for this to work.
        finally:
            self._display_records()
            self._file_loaded = True

    def handle_report_btn(self, event=None) -> None:
        print(self.records_model.get_report())
        self.view.display_popup(title="Report Button",message="Rebort button is not yet implemented")

    def handle_hide_btn(self) -> None:
        self._display_records(hide_found=True)
        found_barcodes = self.records_model.get_found_barcodes()
        if found_barcodes:
            self.barcodes_already_hidden.extend(found_barcodes)

    def handle_show_btn(self) -> None:
        self._display_records(hide_found=False)
        self.barcodes_already_hidden = list()

    def handle_test_btn(self) -> None:
        # generate an existing barcode or a unique barcode at radom with wighting for new barcode as less likely
        # 
        if self._file_loaded == False:
            self.view.display_popup(title="Barcode Simulator",message="You need to load reel data before scanning")
            return
        test_barcode = self.records_model.get_test_barcode()
        if test_barcode == None:
            self.view.display_popup(title="Barcode Simulator",message="Found all barcodes!")
        else:
            self.barcode_scanned(test_barcode)

    def _save_current_progress(self)->None:
        """ Save the current progress of a stocktake test so it can be re-loaded later if need be."""
        json_string = self.records_model.to_json_str()
        try:
            self.file_model.save_progress(self._save_filepath,json_string)
        except FileNotFoundError as e:
            self.view.display_popup(title="Save Progress", message = "File was not found to save progress to.. ")

    def handle_save_btn(self)->None:
        """ Does whatever needs to be done when the save stocktake progress button has been pressed"""
        if self._file_loaded == False:
            self.view.display_popup(title="Save Error",message="Reel data must be loaded before progress can be saved.")
            return
        
        if self._save_filepath == None or self._save_filepath == "":
            # This is the first time a stocktake test has been saved
            self._save_filepath = self.view.create_filepath()

        self._save_current_progress()
        return
        
    def handle_load_stocktake_btn(self):
        load_file_path = self.view.get_filepath()
        try:
            json_string = self.file_model.load_progress(load_file_path)
        except FileNotFoundError as e:
            self.view.display_popup(title="Load Progress", message = "File was not found to load")
        else:
            self.records_model.load_from_json_str(json_string)
            self._file_loaded=True
            self._display_records()

    """ Functions required by the scanner_model"""
    def barcode_scanned(self,barcode:str) -> None:
        """ Processes scanned barcode
            barcode:stl -  Barcode that was scanned by the barcode scanner"""
        # only do anything with a  barcode if a records file has already been loaded
        if self._file_loaded == False:
            self.view.display_popup(title="Barcode Simulator",message="You need to load reel data before scanning")
            return
        
        #insert any unknown barcodes into the stocktake 
        record_exists = self.records_model.barcode_exists(barcode)   
        if not record_exists:
            self.records_model.insert_unknown_reel(barcode)


        #only update the records if the scanned barcode has not already been found
        if not self.records_model.is_record_found(barcode): 
            self.records_model.mark_as_found(barcode)             
        else:
            #barcode has already been found. You are scanning the sambe barcode twice
            self.view.display_popup(title="Barcode Simulator",message=f"Scanned barcode {barcode} has already been found ")


        #Only highlight the barcode if it hasn't been hidden with the hide found option
        if barcode not in self.barcodes_already_hidden:
            if self.records_model.is_record_known(barcode):
                self.view.known_reel_found(barcode)
            else:
                self.view.unknown_reel_found(barcode) 

            self.view.jump_to_barcode(barcode)
            self.view.highlight_barcode(barcode)
        


        