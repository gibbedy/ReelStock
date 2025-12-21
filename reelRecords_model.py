
from __future__ import annotations
from enum import Enum
import random 
from errors import DuplicateBarcodeError
import json
        
class ReelRecord:
    """ dataclass to hold information about a reel of paper"""
    data_names = ["Barcode","Weight","Width","Material"]
    def __init__(self,barcode,weight=None,width=None,material=None,fileID=None):
        #stock data obtained from csv file
        self.barcode:str = barcode
        self.weight:float = weight
        self.width:int = width
        self.material:int = material
        self.fileID:int = fileID

        #stocktake data added by performing a stocktake
        self.found = False          #record has been found during a stocktake
        self.unknownRecord=False    #record is for a reel that was discovered during stocktake (not in the database that was loaded to check stock against)
    def __eq__(self,other):
        return isinstance(other,ReelRecord) and self.barcode == other.barcode
    def __repr__(self):
        description = self.barcode
        return description

    def to_str_list(self)->list[str]:
        """converts a record to a list of strings. one string for each piece of information
            ->list[str]"""
        record_as_list = [self.barcode,str(self.weight),str(self.width),str(self.material),str(self.fileID)]
        return record_as_list
        
    def to_dict(self)->dict:
        """ Convert my reelRecord to a dictionary. Convenient for saving state as a json file"""
        return {"barcode": self.barcode,"weight":self.weight,"width":self.width,"material":self.material,"found":self.found,"unknownRecord":self.unknownRecord,"fileID":self.fileID}
    def get_reel_data(self)->dict:
        """ Return a dictionary of record reel data only."""
        return {k: self.__dict__[k] for k in ("barcode", "weight", "width", "material","fileID")}
    
    def record_from_dict(aDict:dict):
        """ Create a record from a dictionary
            used when loading records that were saved as json"""
        record = ReelRecord(aDict["barcode"],aDict["weight"],aDict["width"],aDict["material"],aDict["fileID"])
        record.found = aDict["found"]
        record.unknownRecord = aDict["unknownRecord"]
        return record
    
class ReelRecords_model:

    """ A collection of ReelRecord's providing functions to manipulate those records"""
    def __init__(self):
        self.records:list[ReelRecord] = [] 
        self.fileID:dict[int,str] = {}   # Map filename where data was loaded from to an id number. id is stored in each reelRecord so we can determine where it came from 

    def clear_records(self):
        """ Clear all records"""
        self.__init__()

    def to_json_str(self)->str:
        """ Convert my reelRecords to a json sting. Convenient for saving state as a json file"""
        return json.dumps({"reelData":[r.to_dict() for r in self.records],"fileID":self.fileID},indent=2)     

    def load_from_json_str(self,json_string:str):
        """ Convert a json string into a reelrecords object"""
        dictRecords = json.loads(json_string) 
        self.records = list()
        for dictRecord in dictRecords["reelData"]:
            record = ReelRecord.record_from_dict(dictRecord)
            self.records.append(record)
        fileID_str_keys:dict[str,str] = dictRecords["fileID"]
        self.fileID:dict[int:str] = {int(k): v for k,v in fileID_str_keys.items()}  #have to restore int-ness of keys as json objects only allow string keys.
            
    def _append(self,record:ReelRecord):
        """ Append a new ReelRecord to the collection"""
        if record.barcode not in [r.barcode for r in self.records]:
            self.records.append(record)
        else:
            raise DuplicateBarcodeError(f"Duplicate barcode: {record.barcode} not inserted")
        
    def findRecord(self,barcode:str)->ReelRecord:
        """ Find record that matches the barcode and return a reference to it
            barcode:str - barcode string to search for
            returns a ReelRecord if a barcode was found, otherwise returns None object"""
        for record in self.records:
            if record.barcode==barcode:
                return record
        return None
     
    def getRandomRecord(self)->ReelRecord:
        """get a random record from the records. Used for testing"""
        random_record = self.records[random.randint(0,len(self.records)-1)]
        return random_record
    
    def allRecordsFound(self) -> bool:
        """ Return True if all records are marked as found"""
        record:ReelRecord = None 
        for record in self.records:
            if record.found == False:
                return False
        return True
    
    def getRandomRecordNotFoundAlready(self)->ReelRecord:
        """ same as getRandomRecord only must return a record that hasn't been found already"""
        if self.allRecordsFound():
            return None
        
        while True:
            record = self.getRandomRecord()
            if record.found!=True:
                break
        return record
        
    def __iter__(self):
        return iter(self.records)
    
    def sort_records(self,sortkey="material"):
        """ Sorts the ReelRecords in place, by the sortkey
            sortkey:str - can only be "material" at the moment"""
        if sortkey=="material":
            self.records.sort(key=lambda r: r.material)

    def sort_by(self,sortKey):
        """ Return records iterrable sorted by sortKey"""
        if sortKey == "weight":
            return sorted(self.records,key = lambda r: r.weight)
        if sortKey == "height":
            return sorted(self.records,key = lambda r: r.width)
        if sortKey == "paperType":
            return sorted(self.records,key = lambda r: r.material)
        
    def getGroups(self,max_group_size=30,hideFound=False):
        """ Return a list of lists of records where each list is a group of records grouped by the sortKey
            if hideFound is true, groups will only contain records that have not been found"""
        groupedList = [[]]
        groupNumber = 0

        sortKey="paperType"
        sortedRecords:list = self.sort_by(sortKey=sortKey)
        

        sortKey = "width" #decided to split groups again by width of reel
        groupValue = getattr(sortedRecords[0],sortKey)
        groupRecordCount = 0
        
        for record in sortedRecords:
            if(hideFound==True):
                if record.found==True:
                    continue
            #keep group sizing small enought to fit on a single window
            groupRecordCount +=1
            if groupRecordCount > max_group_size:
                groupNumber += 1
                groupedList.append([])
                groupRecordCount=0

            recordGroupValue = getattr(record,sortKey)
            if groupValue != recordGroupValue:
                groupNumber += 1
                groupValue = recordGroupValue
                groupedList.append([])
                groupRecordCount=0
            groupedList[groupNumber].append(record)
            
        return groupedList

    def _known_records_count(self)->int:
        count = 0
        for record in self.records:
            if record.unknownRecord==False:
                count+=1
        return count   
    """Functions that must be implemented for the  presenter"""
    def set_records(self,rows:list[list[str]],filepath:str):
        """ loads reel data provided as a list of rows where each list element is column data
            rows:list[list[str]] - reel data to be added to the records
            filepath:str - the filepath where the data was loaded from. """
        
        if filepath not in self.fileID.values():  # only add a filepath if it hasn't already been loaded
            fileID = len(self.fileID)  # assign a fileID to each record that will map to the filepath that was used to load the data.
            self.fileID[fileID] = filepath    # Add a new filepath to the records dictionary that will map the fileID (stored in every record) to the filepath that id refers to.
        else:
            print(f'filepath {filepath} was already in self.fileID')
            fileID = next((k for k, v in self.fileID.items() if v == filepath), None)  # get the key that corresponds to the filepath
            
        duplicateBarcodeErrors = list()    
        for row in rows:
            new_record = ReelRecord(barcode=str(row[0]),width=int(row[1]), weight=int(row[2]),material=str(row[3]),fileID=int(fileID))
            try:
                self._append(new_record)
            except DuplicateBarcodeError as e:
                duplicateBarcodeErrors.append(new_record.barcode)

        if len(duplicateBarcodeErrors) > 0:
            raise DuplicateBarcodeError(duplicateBarcodeErrors)
        else:
            return None    

    def get_records(self,hide_found=False)->list[list[str]]:
        """ Gets all reel records in the form of a list of rows where each list element is column data.
            The first list is the data header names.
            -> list[list[str]]"""
        rows:list[list[str]] = list()
        rows.append(ReelRecord.data_names)
        for record in self.records:
            if hide_found:
                if record.found!=True:
                    rows.append(record.to_str_list())
            else:
                rows.append(record.to_str_list())
        return rows
        
    def barcode_exists(self,barcode:str)->bool:
        """ Returns True if a specified barcode exists in the currently loaded records
            barcode:str - barcode to search for
            -> bool - True if the barcode is found in the records"""
        for record in self.records:
            if record.barcode==barcode:
                return True
        return False
    
    def insert_unknown_reel(self,barcode:str):
        """ Create a new record, with unknown flag marked and append it to the current records
            barcode:str - barcode of reel to be appended to the records"""
        new_record = ReelRecord(barcode=barcode)
        new_record.unknownRecord = True
        self._append(new_record)
    def delete_record(self,barcode:str):
        """Delete a record with the given barcode"""
        for record in self.records:
            if record==ReelRecord(barcode):
                self.records.remove(record)
        
    def mark_as_found(self,barcode:str)->bool:
        """ Find the record containing the barcode parameter and mark it as found
            If the record is found it sets a flag in the record and returns True.
            If the record is not found it returns false"""
        foundRecord = self.findRecord(barcode)
        if foundRecord != None: 
            foundRecord.found=True
            return True
        else:  
            return False
    def mark_as_not_found(self,barcode:str):
        """ Find the record containing the barcode and mark it as not found."""
        foundRecord = self.findRecord(barcode)
        foundRecord.found=False
        
    def get_test_barcode(self)->str:
        unknownBarcodes=["5318008","112358132Z","2997924589"] #test barcodes that won't be in the records  
        if random.randint(0,10)==0:
            return unknownBarcodes[random.randint(0,2)]
        else:
            random_record = self.getRandomRecordNotFoundAlready()
            if random_record == None:
                return None
            else:
                return random_record.barcode
        
    def get_found_barcodes(self)->list[str]|None:
        """ Return a list of barcodes which have already been found
            returns: list[str]"""
        return [r.barcode for r in self.records if r.found]
        
    def get_unknown_barcodes(self)->list[str]|None:
        """ Return a list of barcodes which are unknown
            returns: list[str]"""
        return [r.barcode for r in self.records if r.unknownRecord]
    
    def get_found_unknown_barcodes(self)->list[str]:
        return [r.barcode for r in self.records if r.unknownRecord and r.found]

    def get_found_known_barcodes(self)->list[str]:
        return [r.barcode for r in self.records if not r.unknownRecord and r.found]

    def is_record_known(self,barcode:str)->bool:
        for record in self.records:
            if record.barcode==barcode and record.unknownRecord==False:
                return True
        return False
    def is_record_unknown(self,barcode:str)->bool:
        for record in self.records:
            if record.barcode==barcode and record.unknownRecord==True:
                return True
        return False
    
    def is_record_found(self,barcode:str)->bool:
        for record in self.records:
            if record.barcode==barcode and record.found==True:
                return True
        return False
    def get_report(self)->dict:
        """ Return a summary of the stocktake"""
        found_known_barcodes = self.get_found_known_barcodes()
        found_unknown_barcodes = self.get_found_unknown_barcodes()

        known_record_count = self._known_records_count()
        report = dict()
        report["found_count"] = len(found_known_barcodes)
        report["unknown_count"] = len(found_unknown_barcodes)
        report["missing_count"] = known_record_count - len(found_known_barcodes)
        report["missing_reels"] = [r.get_reel_data() for r in self.records if r.found==False]
        report["unknown_reels"] = [r.get_reel_data() for r in self.records if (r.unknownRecord and r.found==True)]
        return report

    def get_fileID(self)->dict[int,str]:
        """ Return the fileID dictionary"""
        return self.fileID
    def _check_barcode_is_valid_looking(barcode:str):
        if len(barcode) != 10:
            return False
        return True
