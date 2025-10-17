from tk_view import Tk_view
from reelRecords_model import ReelRecords_model
from stocktake_presenter import Stocktake_presenter
from fileAccess_model import FileAccess_model
from scanner_z3678_model import Scanner_z3678_model
import sys
from pathlib import Path

def main() -> None:
    reelRecords_model = ReelRecords_model()
    fileAccess_model = FileAccess_model()
    tk_view = Tk_view()
    scanner_z3768_model = Scanner_z3678_model()
    stocktake_presenter = Stocktake_presenter(fileAccess_model,reelRecords_model,tk_view,scanner_z3768_model)
    file_paths = [str(Path(p)) for p in sys.argv[1:]] # get file paths for files dragged and dropped onto exe
    stocktake_presenter.set_file_paths(file_paths)
    
    
    stocktake_presenter.run()

if __name__ == "__main__":
    main()