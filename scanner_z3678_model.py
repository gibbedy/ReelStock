from typing import Any,Callable,Protocol

class Presenter(Protocol):
    """ interface to the Presenter. That is functions that the presenter must implement for interaction with the scanner"""
    def barcode_scanned(self,barcode:str):
        ...

class Scanner_z3678_model:
    ...

    """Functions that must be implemented for the  presenter"""
    def startScanner(self,presenter:Presenter):
        ...