class StocktakeError(Exception):pass
class DuplicateBarcodeError(StocktakeError):pass
class DatafileNotLoadedError(StocktakeError):pass
