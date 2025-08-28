from tkinter import Tk,PhotoImage,Frame,Button,Text,messagebox,NORMAL,END,INSERT,DISABLED
from typing import Any,Callable,Protocol
from tkinter.filedialog import askopenfilename,asksaveasfilename
from tkinter.ttk import Treeview,Scrollbar,Style
#Here I set the interface that the presenter must use. 
#I believe it forces compile time checking so i know if i haven't implemented something in my
#Stocktake_presenter that needs to be implemented
class Presenter(Protocol):
    """ interface to the Presenter. That is functions that the presenter must implement"""
    def handle_load_btn(self) -> None:
        ...
    def handle_report_btn(self) -> None:
        ...
    def handle_hide_btn(self) -> None:
        ...
    def handle_show_btn(self) -> None:
        ...
    def handle_test_btn(self) -> None:
        ...
    def handle_save_btn(self) -> None:
        ...
    def handle_load_stocktake_btn(self) -> None:
        ...
    
class Tk_view(Tk):
    def __init__(self)->None:
        super().__init__()
        self.title("Reel Stocktake")
        scanIcon=PhotoImage(file="assets/icons/Zebra64.png")
        self.iconphoto(True,scanIcon)
        self.style = Style(self)

        # Create or configure a style for Treeview
        self.style.configure("Treeview", font=("TkDefaultFont", 14))         # table text
        self.style.configure("Treeview.Heading", font=("TkDefaultFont", 14)) # header text

        # ✅ Make root grid expandable
        self.rowconfigure(1, weight=1)      # the row where recordsFrame lives
        self.columnconfigure(0, weight=1)   # the only column

    def show_help(self,message:str):
        """ put a message in a Text box
        textbox: the Text box object that you want to put the message in
        message: the string to put in the text box"""
        self.infoTextBox.config(state=NORMAL)  # text box is probably disabled to prevent input before this command was given
        self.infoTextBox.delete("1.0",END) #clear the textbox
        self.infoTextBox.insert(INSERT,message)
        self.infoTextBox.config(state=DISABLED)

    def set_help(self,aButton:Button,hlp_message:str):
            """ assign help text for a givent widget to a the info text box.
                aButton: A reference to a ttk.Button (will work for any widget that supports bind) that you want to have a tooltip for
                hlp_message: A string of text that will appear in the help textbox"""     
            aButton.bind("<Enter>", lambda e: self.show_help(hlp_message))
            aButton.bind("<Leave>", lambda e: self.clear_help())

    def clear_help(self):
        self.show_help("")

    """Functions that must be implemented for the  presenter"""
    def create_ui(self,presenter:Presenter):
        """Creates all components of the tkinter user interface"""

        self.menuFrame = Frame(master=self)

        self.recordsFrame = Frame(master=self)
        self.recordsFrame.grid(row=1)
        self.recordsFrame.columnconfigure(0,weight=1)
        self.recordsFrame.rowconfigure(0,weight=1)

        self.menuFrame.grid(row=0, sticky="ew")     # ✅ stretch horizontally

        self.recordsFrame = Frame(master=self)
        self.recordsFrame.grid(row=1, sticky="nsew")  # ✅ fill all available space

        menuPadx=3
        # Or explicitly for all Labels only
        self.option_add("*Label.Font", ("TkDefaultFont", 13))
        self.infoTextBox = Text(master=self.menuFrame,width=100,height=8)
        #self.infoTextBox.grid(row=0,column=0,padx=5)

        #infoTextBox = Text(master=recordsFrame,width=150)
        startupInfo = ("1 - Export Reel stock information from SAP as an Excel spreadsheet\n" +
                        "2 - Press the 'Load' button above and select the file exported in the previous step\n" +
                        "    Reel data will be loaded from the spreadsheet and grouped by 'Material' and 'Batch width'\n" +
                        "3 - Plug in the Zebra DS3678-XR barcode scanner base and scan reel barcodes\n" +
                        "    - Scanned barcodes will change color to green\n"
                        "    - Unknown barcodes will be inserted and appear as orange\n"+
                        "5 - Press 'Report' button to show missed and unknown reels")

        self.infoTextBox.insert("1.0",startupInfo)
        self.set_help(self.infoTextBox,startupInfo)
        sample_x = 8
        sample_y = 8
        self.testButtonImg = PhotoImage(file="assets/icons/Ai_Scan_Barcode.png").subsample(sample_x,sample_y)
        self.loadButtonImg = PhotoImage(file="assets/icons/Ai_Load_Reel_Data.png").subsample(sample_x,sample_y)
        self.reportButtonImg = PhotoImage(file="assets/icons/Ai_Stocktake_Report.png").subsample(sample_x,sample_y)
        self.hideButtonImg = PhotoImage(file="assets/icons/Ai_Hide_Found_Reels.png").subsample(sample_x,sample_y)
        self.showButtonImg = PhotoImage(file="assets/icons/Ai_Show_Found_Reels.png").subsample(sample_x,sample_y)
        self.saveProgressImg = PhotoImage(file="assets/icons/Ai_Save_Progress.png").subsample(sample_x,sample_y)
        self.loadStocktakeImg = PhotoImage(file="assets/icons/Ai_Load_Test.png").subsample(sample_x,sample_y)

        self.loadButton = Button(master=self.menuFrame,text="Load",command=presenter.handle_load_btn, image=self.loadButtonImg)
        self.loadButton.grid(row=0,column=1,padx=menuPadx)
        self.set_help(self.loadButton,"Opens an Excel spreadsheet file.\n" +
                            "The Reel data is appended to any data already loaded\n" +
                            "This will allow loading of multiple seperate spreadsheets which is something Jan says is required")

        self.reportButton = Button(master=self.menuFrame,text="Show Report",command=presenter.handle_report_btn, image=self.reportButtonImg)
        self.reportButton.grid(row=0,column=2,padx=menuPadx)
        self.set_help(self.reportButton,"Create a report showing missing reels or unknown reels.\n" +
                            "Not implemented yet\n")

        self.hideButton = Button(master=self.menuFrame,text="Hide Found Reels",command=presenter.handle_hide_btn,image=self.hideButtonImg)
        self.hideButton.grid(row=0,column=3,padx=menuPadx)
        self.set_help(self.hideButton,"Hide any reels that have already been scanned")

        self.showButton = Button(master=self.menuFrame,text="Show Found Reels",command=presenter.handle_show_btn, image=self.showButtonImg)
        self.showButton.grid(row=0,column=4,padx=menuPadx)
        self.set_help(self.showButton,"Show all reels if they have been hidden with hide reels")

        self.testButton = Button(master=self.menuFrame,text="Random Barcod Scan Simulation Button",command=presenter.handle_test_btn,image=self.testButtonImg)
        self.testButton.grid(row=0, column=5,padx=menuPadx)
        self.set_help(self.testButton,"This button simulates a scann of a random barcode from the data\n" +
                            "Simulator will randomly scan a barcode that is not in the database to simulate finding a new Reel.\n" +
                            "Found items will be highlighted in green, new reels found will be highlighted in orange at the end of the list"
                            "This button will be removed when we have the scanner hardware")
        
        self.saveProgressButton = Button(master=self.menuFrame,text="Save Progress",command=presenter.handle_save_btn,image=self.saveProgressImg)
        self.saveProgressButton.grid(row=0, column=6,padx=menuPadx)
        self.set_help(self.saveProgressButton,"Save the current stocktake results so it can be continued at a later time.")

        self.loadStocktakeButton = Button(master=self.menuFrame,text="Save Progress",command=presenter.handle_load_stocktake_btn,image=self.loadStocktakeImg)
        self.loadStocktakeButton.grid(row=0, column=7,padx=menuPadx)
        self.set_help(self.loadStocktakeButton,"Load a previously saved stocktake.")
                           
    def get_filepath(self)->str:
        return askopenfilename(title="Open Reel Data Excel File")
    
    def create_filepath(self)->str:
        return asksaveasfilename(title="Save stocktake progress to this file")
    
    def display_records(self,records)->None:
        """ Display records in the gui.
            records:list[list[str]] - two dimensional list.. rows of column data"""
        
        self.iid_to_barcode_map = dict() # Used for mapping treeview rows to the barcode that it contains, so I can toggle colors based on barcodes.

        cols = records[0]
        data = records[1:]

        
        self.records_tree = Treeview(master=self.recordsFrame,columns=cols,show="headings")
        # configure tags (like "classes" of style)
        self.records_tree.tag_configure("green", background="lightgreen")
        self.records_tree.tag_configure("orange", background="orange")
        self.records_tree.tag_configure("error", background="red", foreground="white")
        # Set headings from the same list
        for col in cols:
            self.records_tree.heading(col, text=col)
        
        for col in cols:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, stretch=True)  # ✅ ensure columns expand

        # Insert data rows
        for row in data:
            iid = self.records_tree.insert("", "end", values=row)
            self.iid_to_barcode_map[row[0]] = iid

        # Create vertical scrollbar
        scrollbar = Scrollbar(master=self.recordsFrame, orient="vertical", command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)

        # Layout: Treeview on left, scrollbar on right
        self.records_tree.grid(row=0, column=0, sticky="nse")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Make sure the treeview expands with the frame
        self.recordsFrame.rowconfigure(0, weight=1)
        self.recordsFrame.columnconfigure(0, weight=0)    

    def unknown_reel_found(self,barcode:str):
        """ Insert an unkown reel into the table and mark it orange
            barcode:str - barcode of the reel to be inserted"""
        if barcode not in self.iid_to_barcode_map.keys():      
            self.iid_to_barcode_map[barcode] = self.records_tree.insert("", "end", values=[barcode,"","",""])
        iid = self.iid_to_barcode_map[barcode]
        self.records_tree.item(iid, tags="orange",)
        
    def known_reel_found(self,barcode:str):
        """ Mark reel in the table green"""
        iid = self.iid_to_barcode_map[barcode]  
        self.records_tree.item(iid, tags="green",)
    
    def display_popup(self,title:str,message:str):
        messagebox.showinfo(title=title,message=message)

    def jump_to_barcode(self,barcode:str)->None:
        """move the treeview to the position of the barcode"""
        iid = self.iid_to_barcode_map[barcode]
        self.records_tree.see(iid)
    def highlight_barcode(self,barcode:str)->None:
        """ Highlight the barcode in the treeview"""
        self.records_tree.selection_set(self.iid_to_barcode_map[barcode])
