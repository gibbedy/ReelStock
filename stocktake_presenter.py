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
    def show_report(self,found_count:int, unknown_count:int, missing_count:int, missing_reels:list[dict], unknown_reels:list[dict]):
        ...
    def setTitle(self,title:str)->None:
        ...
    def display_popup_yes_no(self,title:str,message:str,detail:str)->bool:
        ...
    def set_file_legend(self,fileID:dict[int,str]):
        ...
    def copy_lines_to_clipboard(self,lines:list[str]):
        ...

class File_model(Protocol):
    """ Interface to the file model for file i/o"""
    def get_rows(self)->list[list[str]]:
        ...
    def save_progress(self, filepath:str,json_records:str)->None:
        ...
    def load_progress(self, filepath:str)->None:
        ...

    def log_scanned_barcode(self, barcode: str):
        ...

class Records_model(Protocol):
    """ Interface to the records model"""
    def set_records(self,rows:list[list[str]],filepath:str)->None:
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
    def clear_records(self)->None:
        ...
    def get_fileID(self)->dict[int,str]:
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
    
    def _reset(self)->None:
        """ Reset presenter variables.
            Do this before loading a previously saved stocktake test"""
        self._file_loaded=False
        self._save_filepath = None
        self.filepath = None
        self.barcodes_already_hidden = list()
        self.records_model.clear_records()

    def run(self)->None:
        self.view.create_ui(self)
        self._display_records()
        self.scanner_model.startScanner(self)
        self.view.mainloop()
    
    def _update_file_legend(self):
        """update the legend for each of the files loaded"""
        fileID = self.records_model.get_fileID()
        self.view.set_file_legend(fileID)

    def _display_records(self,hide_found:bool = False)->None:
        """Fetch all record rows from the records_model and send them to view for displaying."""
        rows = self.records_model.get_records(hide_found=hide_found)
        self.view.display_records(rows)
        self._update_file_legend()

        found_known_reels = self.records_model.get_found_known_barcodes()
        found_unknown_reels = self.records_model.get_found_unknown_barcodes()

        if hide_found==False:
            for barcode in found_unknown_reels:
                self.view.unknown_reel_found(barcode)
    
            for barcode in found_known_reels:
                self.view.known_reel_found(barcode)
                

    def _append_or_overwrite(self)->bool:
        """ Clears reelRecords data based on user response to a window popup messagebox
            ->bool Returns True unless the user chose not to proceed with the loading during when asked by popup message"""
        if self._file_loaded == True:
            append = self.view.display_popup_yes_no(title="Load File",message="Do you want to append data to existing data?",
                                            detail= "Choosing Yes adds stocktake data to the current data, any duplicate records are ignored " +
                                                "choosing No clears all the stocktake data that was already loaded previously")
            if not append:
                answer = self.view.display_popup_yes_no(title="Load File", message = "Are you sure you want todo this?",
                                                        detail="Pressing yes will clear the data currently loaded")
                if answer:
                    self._reset()
                    self._file_loaded = False
                else:
                    return False
                
            
        return True
    
    """functions required by the view"""
    def handle_load_btn(self) -> None:
        """Load an excel file of reel data into the reelRecords model."""
        if self._append_or_overwrite():
            self.filepath = self.view.get_filepath()
        else:
            return
        try:
            rows = self.file_model.get_rows(self.filepath) 
        except FileNotFoundError as e:
            self.view.display_popup(title="Load File", message = "File wasn't found, or you didn't select a file")
        except ValueError as e:
            self.view.display_popup(title="Load File", message = "Failed to load a file due to valueError.  Load button expects an Exel file format. Were you loading the correct file?")
        else: # Successfully loaded a file which is stored in rows so we can try creating reel records from this
            self._file_loaded = True
            try:
                self.records_model.set_records(rows,filepath=self.filepath)
            except  DuplicateBarcodeError as e:
                self.view.display_popup(title="Load File Error", message="The following is a list of reels that were NOT inserted because they have the same ID as a one already loaded:\n " + str(e)) #need to convert set records exeptions to a single string i think for this to work.
        finally: # A failed loading of data into rows, or a success, either way we need to display records to either display the new data or clear the previously displayed data
            self._display_records()
            
            self.view.setTitle(f"Loaded file: {self.filepath}")

    def handle_report_btn(self, event=None) -> None:
        report = self.records_model.get_report()
        
        self.view.show_report(found_count=report["found_count"],unknown_count=report["unknown_count"], missing_count=report["missing_count"], missing_reels=report["missing_reels"],unknown_reels=report["unknown_reels"])
        #self.view.display_popup(title="Report Button",message="Rebort button is not yet implemented")

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
        except PermissionError as e:
            self.view.display_popup(title="Load Progress", message = "Permission Error while trying to open the stocktake file")
        except UnicodeDecodeError as e:
            self.view.display_popup(title="Load Progress", message = "Failed to decode file. Maybe you opened the wrong file.")

        else:
            self.records_model.load_from_json_str(json_string)
            self._file_loaded=True
            self._display_records()

    def handle_scanner_code(self,barcode:str) -> None:
        self.barcode_scanned(barcode=barcode)

    def handle_copy_missing_btn(self):
        """ Copy missing reels data to the clipboard"""
        report = self.records_model.get_report()
        reel_data_text = self._convert_dict_list_to_str(report["missing_reels"])
        self.view.copy_lines_to_clipboard(reel_data_text)
        
    def handle_copy_unknown_btn(self):
        """ Copy unknown reels data to the clipboard"""
        report=self.records_model.get_report()
        reel_data_text = self._convert_dict_list_to_str(report["unknown_reels"])
        self.view.copy_lines_to_clipboard(reel_data_text)
        
    """ Functions required by the scanner_model"""
    def barcode_scanned(self,barcode:str) -> None:
        """ Processes scanned barcode
            barcode:stl -  Barcode that was scanned by the barcode scanner"""
        self.file_model.log_scanned_barcode(barcode)
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

    def _convert_dict_list_to_str(self, list_dict:list[dict[list]]) ->str:
        """ Returns a string representation of a list of dictionaries 
            Each item of the dictionary is seperated by a tab.
            Each dictionary in the list is seperated by a carriage return"""  
        txt = "\n".join("\t".join(str(value) for value in a_dict.values()) for a_dict in list_dict)
        return txt
    
    