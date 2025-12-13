from __future__ import annotations
from typing import Protocol
from errors import DuplicateBarcodeError
from datetime import datetime
from fileAccess_model import resource_path
class View(Protocol):
    """ interface to the view model for gui. That is functions that the view must implement"""
    def mode_selection_window(self,presenter:Stocktake_presenter)->None:
        ...
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
    def clear_found(self,barcode:str):
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
    def alert_bell(self)->None:
        ...
    def append_message(self,message:str)->None:
        ...
    def close(self)->None:
        ...
    def delete_record(self,barcode:str)->None:
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
    def get_latest_save_path(self)->str:
        ...
    def get_old_save_paths(self,num_of_files_to_keep:int)->list[str]:
        ...
    def delete_file(self,filepath):
        ...
    def archive_tests(self)->None:
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
    def mark_as_not_found(self,barcode:str):
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
    def is_record_unknown(self,barcode:str)->bool:
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
    def delete_record(self,barcode:str):
        ...   
class Scanner_model(Protocol):
    """ Interface to the barcode scanner model"""
    def startScanner(self,presenter:Stocktake_presenter) -> None:
        ...
class Sound_model(Protocol):
    def play_duplicate_bc(self):
        ...
    def play_unknown_bc(self):
        ...
    def play_found_bc(self):
        ...
    def play_incorrect_bc(self):
        ...

class Stocktake_presenter:

    AUTOSAVE_COUNT = 1                  #Autosave will happen after this many scans
    AUTOSAVE_COUNT_NEW_FILE = 10        #Autosave will create a new file after this many autosaves have been done

    def __init__(self,file_model:File_model,records_model:Records_model,view:View,scanner_model:Scanner_model,sound_model:Sound_model):
        self.file_model = file_model
        self.records_model = records_model
        self.view = view
        self.scanner_model = scanner_model
        self.sound_model = sound_model
        self._file_loaded = False 
        self._save_filepath = None
        self.filepath = None
        self.barcodes_already_hidden = list() 

        self.scan_count = 0             #count of current scans that have been done
        self.file_paths = []            #file path arguments that were passed on loading app. (for dragging xls file onto exe )

    def set_file_paths(self,paths:list[str]):
        self.file_paths = paths

    def _reset(self)->None:
        """ Reset presenter variables.
            Do this before loading a previously saved stocktake test"""
        self._file_loaded=False
        self._save_filepath = None
        self.filepath = None
        self.barcodes_already_hidden = list()
        self.records_model.clear_records()

    def run(self)->None:
        if not self.file_paths:
            self.continue_existing_btn()    # No file paths were passed on startup, so we are continuing and existing stocktake test
        else:
            self.handle_start_new_btn()     # A filepath was passed that needs to be loaded as a new stocktake test

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
    def continue_existing_btn(self):
        self.view.create_ui(self)
        self._display_records()
        self.auto_load_save_file()

    def handle_start_new_btn(self):
        self.view.create_ui(self)
        self._display_records()
        self.handle_autoload(self.file_paths)

    def handle_load_btn(self) -> None:
        """Load an excel file of reel data into the reelRecords model."""
        if not self._append_or_overwrite():
            return
        self.manual_load_xls()
        
    def manual_load_xls(self) -> None:
        """Load an excel file of reel data into the reelRecords model."""
        self.filepath = self.view.get_filepath()
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

    def handle_autoload(self,paths)->None:
        """Automatically loads stocktake data if a path was available on bootup in sys.argv[1:]
            This gives the ability to drag an xls file onto the pyinstaller executeable and have it load"""
        for path in paths:
            try:
                rows = self.file_model.get_rows(path) 
            except FileNotFoundError as e:
                self.view.display_popup(title="Load File", message = "File wasn't found, or you didn't select a file")
            except ValueError as e:
                self.view.display_popup(title="Load File", message = "Failed to load a file due to valueError.  Load button expects an Exel file format. Were you loading the correct file?")
            else: # Successfully loaded a file which is stored in rows so we can try creating reel records from this
                self._file_loaded = True
                try:
                    self.records_model.set_records(rows,filepath=path)
                except  DuplicateBarcodeError as e:
                    self.view.display_popup(title="Load File Error", message="The following is a list of reels that were NOT inserted because they have the same ID as a one already loaded:\n " + str(e)) #need to convert set records exeptions to a single string i think for this to work.
                else:
                    ...
                    self.file_model.archive_tests() 
                    self._autosave()    
            finally: # A failed loading of data into rows, or a success, either way we need to display records to either display the new data or clear the previously displayed data
        
                self._display_records()
        
                self.view.setTitle(f"Loaded file: {paths}")

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
            self.view.display_popup(title="Save Progress", message = f"File was not found to save progress to:{self._save_filepath} ")
            self._send_message(message="failed  saved",bell=False)
        else:
            ...
            #self._send_message(message="Progress saved",bell=False)
    
    def handle_save_btn(self)->None:
        """ Does whatever needs to be done when the save stocktake progress button has been pressed"""
        if self._file_loaded == False:
            self.view.display_popup(title="Save Error",message="Reel data must be loaded before progress can be saved.")
            return
        
        if self._save_filepath == None or self._save_filepath == "":
            # This is the first time a stocktake test has been saved
            self._save_filepath = "save_file_"+str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

        self._save_current_progress()
        return
        
    def _autosave(self)->None:
        if (self.scan_count % self.AUTOSAVE_COUNT_NEW_FILE) == 0:
            self._save_filepath=None
            self.handle_save_btn()
            files_to_delete = self.file_model.get_old_save_paths(num_of_files_to_keep=3)
            for f in files_to_delete:
                self.file_model.delete_file(f)
        elif (self.scan_count % self.AUTOSAVE_COUNT) == 0:
            self.handle_save_btn()
        return

    def handle_load_stocktake_btn_old(self):
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
            self._save_filepath = None #reset existing safe filepath if one exists
            self._file_loaded=True
            self._display_records()

    def auto_load_save_file(self):
        
        load_file_path = self.file_model.get_latest_save_path()
            
        try:
            json_string = self.file_model.load_progress(load_file_path)
        except FileNotFoundError as e:
            load_new_file = self.view.display_popup_yes_no(title="Auto Load Progress failed", message=f"Auto-load failed to find a save file {load_file_path}, do you want to start a new stocktake"
                                           ,detail="Clicking yes will open a dialog box where you need to find the excel spreadhseet exported from sap." +
                                           "\n Clicking No will close the application")
            if load_new_file:
                self.manual_load_xls()
                if not self._file_loaded:
                    self.auto_load_save_file()
                else:
                    self._autosave()
            else:
                self.view.close()
            #self.view.display_popup(title="Load Progress", message = f"File: {load_file_path} was not found to load")
        except PermissionError as e:
            self.view.display_popup(title="Load Progress", message = "Permission Error while trying to open the stocktake file")
        except UnicodeDecodeError as e:
            self.view.display_popup(title="Load Progress", message = "Failed to decode file. Maybe you opened the wrong file.")

        else:
            self.records_model.load_from_json_str(json_string)
            self._save_filepath = None #reset existing safe filepath if one exists
            self._file_loaded=True
            self._display_records()
            self._send_message(message=f"Loaded previous save file:\n-{load_file_path}\t")

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

    def handle_pretend_found(self,barcode:str):
        
        if not self.records_model.is_record_found(barcode): 
            self.barcode_scanned(barcode=barcode)
        else:
            self._barcode_clear_found(barcode=barcode)
            ### need to add logic to clear the green. need to think about this.........................................................

    def handle_manual_entry(self,barcode:str):
        if self.barcode_scanned(barcode=barcode.upper()):
            self._send_message(f"Manually inserted barcode: {barcode}")

    def _barcode_clear_found(self,barcode:str):
        """Mark the record with the corresponding barcode as not found and update the view"""   
        if self.records_model.is_record_unknown(barcode=barcode):   #unknown records are deleted. User must have scanned an unknown barcode that they now want to remove
            self.records_model.delete_record(barcode=barcode)   
            self.view.delete_record(barcode=barcode)
            self._autosave()


        if self.records_model.is_record_known(barcode=barcode):    
            self.records_model.mark_as_not_found(barcode=barcode)
            self.view.clear_found(barcode)
            self._autosave()

    def _log_scanned_barcode(self,barcode:str):
        self.file_model.log_scanned_barcode(barcode)

    def _check_data_loaded(self)->bool:
        if self._file_loaded == False:
            self.view.display_popup(title="Barcode Simulator",message="You need to load reel data before scanning")
            return False
        else:
            return True

    def _duplicate_barcode_alert(self,barcode)->None:
        #self.view.alert_bell()
        self.sound_model.play_duplicate_bc()
        self._send_message(message=f"Duplicate Barcode of {barcode}\t\t scanned",bell=False)

    def _send_message(self,message:str,bell=True):
        if bell:
            self.view.alert_bell()
        self.view.append_message(message + "\t" + str(datetime.now()))

    """ Functions required by the scanner_model"""
    def _check_barcode_is_valid_looking(self,barcode):
        if len(barcode) < 5:
            yes_no = self.view.display_popup_yes_no(title="Invalid Barcode?",message="Are you sure you sure you want to insert this short barcode?", detail="A.I. detected that the barcode was invalid")
            if(not yes_no):
                self._send_message(message=f"Did not insert barcode {barcode}",bell=False)
                self.sound_model.play_incorrect_bc()
                return False
        
        return True
    
    def barcode_scanned(self,barcode:str) -> bool:
        """ Processes scanned barcode
            barcode:stl -  Barcode that was scanned by the barcode scanner
            -> Returns false if there was an issue with the barcode"""
        result = True

        if not self._check_barcode_is_valid_looking(barcode):
            return False
        
        self._log_scanned_barcode(barcode=barcode)

        # only do anything with a  barcode if a records file has already been loaded
        if not self._check_data_loaded():
            return False
        
        #insert any unknown barcodes into the stocktake 
        record_exists = self.records_model.barcode_exists(barcode)   
        if not record_exists:
            self.records_model.insert_unknown_reel(barcode)

        #only update the records if the scanned barcode has not already been found
        if not self.records_model.is_record_found(barcode): 
            self.records_model.mark_as_found(barcode)             
        else:
            #barcode has already been found. You are scanning the same barcode twice
            self._duplicate_barcode_alert(barcode=barcode)
            result=False
            
        #Only highlight the barcode if it hasn't been hidden with the hide found option
        if barcode not in self.barcodes_already_hidden:
            if self.records_model.is_record_known(barcode):
                self.view.known_reel_found(barcode)
                self.sound_model.play_found_bc()
            else:
                self.view.unknown_reel_found(barcode) 
                self.sound_model.play_unknown_bc()

            self.view.jump_to_barcode(barcode)
            self.view.highlight_barcode(barcode)

        self.scan_count += 1
        self._autosave()
        return result
    def _convert_dict_list_to_str(self, list_dict:list[dict[list]]) ->str:
        """ Returns a string representation of a list of dictionaries 
            Each item of the dictionary is seperated by a tab.
            Each dictionary in the list is seperated by a carriage return"""  
        txt = "\n".join("\t".join(str(value) for value in a_dict.values()) for a_dict in list_dict)
        return txt
    
    