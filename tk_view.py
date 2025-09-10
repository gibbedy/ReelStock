from tkinter import Tk,PhotoImage,Frame,Button,Text,messagebox,Toplevel,Label,NORMAL,END,INSERT,DISABLED,Event
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
    def handle_scanner_code(self) -> None:
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

        self.capture_scanner(presenter)

    def capture_scanner(self,presenter):
        """ Setup how this view will detect a scanner event.
            I'm thinking listening for a code followed by a carriage return on the keyboard"""    

        self.scanner_buffer = []

        def on_key(event:Event):
            # If Enter pressed, process the buffer
            if event.keysym == "Return":
                code = "".join(self.scanner_buffer).strip()
                self.scanner_buffer.clear()
                if code:
                    presenter.handle_scanner_code(code)  # you define this
            else:
                # Ignore modifier keys, arrows, etc.
                if len(event.char) == 1 and event.char.isprintable():
                    self.scanner_buffer.append(event.char)

        # Bind at the application (root) level
        self.bind("<Key>", on_key)   

    def get_filepath(self)->str:
        return askopenfilename(title="Open Reel Data Excel File")
    
    def create_filepath(self)->str:
        return asksaveasfilename(title="Save stocktake progress to this file")
    
    def show_report(self,found_count:int, unknown_count:int, missing_count:int, missing_reels:list[dict], unknown_reels:list[dict]):
        """ Display a report in a new window showing the completed stocktake results.
            
            found_count:int - The number of reels from the stocktake records that were found
            unknown_count:int - The number of new reels found that were not in the stocktake records
            missing_count:int - The number of reels that were not found from the stocktake records
            missing_reels:list[dict] - reel data for the missing reels in the form of a list of dictionaries. Each dictionary is one reels information
            unknown_reels:list[dict] - reel data for the reels found that were not in the stocktake data. Each dictionary is one reels information """
        
        report_window = Toplevel()
        report_window.title(f'Stocktake Report')
        report_window.rowconfigure(0,weight=1)
        report_window.columnconfigure(0,weight=1)

        whole_frame = Frame(report_window,bg="white")
        whole_frame.grid()

        whole_frame.grid_rowconfigure(0,weight=1)
        whole_frame.grid_columnconfigure(0,weight=1)


        stats_frame = Frame(whole_frame,bg="white",bd=2, relief="solid")
        stats_frame.grid(row=0,column=0,padx=5,pady=5)


        unknown_reels_frame = Frame(whole_frame,bg="white",bd=2, relief="solid")
        unknown_reels_frame.grid(row=1,column=0,padx=5,pady=5)

        # Make sure the treeview expands with the frame
        unknown_reels_frame.rowconfigure(1, weight=1)
        unknown_reels_frame.columnconfigure(0, weight=0)  

        missing_reels_frame = Frame(whole_frame,bg="white",bd=2, relief="solid")
        missing_reels_frame.grid(row=2,column=0,padx=5,pady=5)

        # Make sure the treeview expands with the frame
        missing_reels_frame.rowconfigure(1, weight=1)
        missing_reels_frame.columnconfigure(0, weight=0)

        style = Style()
        style.theme_use("clam")   # clam respects bg colors better
        style.configure("Stats.Treeview",
                background="yellow",    # row background
                fieldbackground="yellow",  # empty space
                foreground="black")          # text color
        
        style.configure("Stats.Treeview.Heading",
                background="yellow",    # row background
                fieldbackground="yellow",  # empty space
                foreground="black")          # text color
        
        style.configure("Unknown.Treeview",
                background="pink",    # row background
                fieldbackground="pink",  # empty space
                foreground="black")          # text color
        
        style.configure("Stats.Treeview.Heading",
                background="pink",    # row background
                fieldbackground="pink",  # empty space
                foreground="black")          # text color
        
        
        style.configure("Missing.Treeview",
                background="green",    # row background
                fieldbackground="green",  # empty space
                foreground="black")          # text color
        
        style.configure("Stats.Treeview.Heading",
                background="green",    # row background
                fieldbackground="green",  # empty space
                foreground="black")          # text color
        
        

        stats_title=Label(master=stats_frame,text="Stocktake Stats")
        stats_title.config(bg=stats_title.master["bg"])

        stats_title.grid(row=0,column=0)

        stats_tree = Treeview(master=stats_frame,columns=["stat","count"], show="headings")

        stats_tree.grid(row=1, column=0, sticky="nsew")

        stats_tree.heading("stat", text="Stat")
        stats_tree.column(column="stat", stretch=True,width=400)
        stats_tree.heading("count", text="Count")
        stats_tree.column(column="count",stretch=True,width=150)

        stats_tree.insert(parent="",index="end",values=("Number of Reels Found",found_count))
        stats_tree.insert(parent="",index="end",values=("Number of Unknown Reels Found",unknown_count))
        stats_tree.insert(parent="",index="end",values=("Number of Reels Not Found",missing_count))

        unknown_title=Label(master=unknown_reels_frame,text="Reels found that were not in the stocktake data")
        unknown_title.grid(row=0,column=0)
        unknown_title.config(bg=unknown_title.master["bg"])

        if len(unknown_reels) > 0:
            column_headings = [key for key in unknown_reels[0].keys()]
            unknown_reels_tree = Treeview(master=unknown_reels_frame,columns=column_headings,show="headings")

            unknown_reels_tree.grid(row=1,column=0,padx=10,pady=10)

            for heading in column_headings:
                unknown_reels_tree.heading(heading, text=heading)
                unknown_reels_tree.column(column=heading, stretch=True,width=400)

            for reel in unknown_reels:
                print(f'reel in unknown reels is of type {type(reel)} and has a value of {reel}')
                unknown_reels_tree.insert(parent="",index="end",values=list(reel.values()))

        
        missing_title=Label(master=missing_reels_frame,text="Reels not found in the stocktake")
        missing_title.config(bg=missing_title.master["bg"])

        missing_title.grid(row=0,column=0)
        if len(missing_reels) > 0:
            column_headings = [key for key in missing_reels[0].keys()]
            missing_reels_tree = Treeview(master=missing_reels_frame,columns=column_headings,show="headings")
            missing_reels_tree.grid(row=1,column=0,padx=10,pady=10, sticky="nse")

            for heading in column_headings:
                missing_reels_tree.heading(heading, text=heading)
                missing_reels_tree.column(column=heading, stretch=True,width=400)

            for reel in missing_reels:
                print(f'reel in unknown reels is of type {type(reel)} and has a value of {reel}')
                missing_reels_tree.insert(parent="",index="end",values=list(reel.values()))

        # Create vertical scrollbar
        missing_scrollbar = Scrollbar(master=missing_reels_frame, orient="vertical", command=missing_reels_tree.yview)
        missing_reels_tree.configure(yscrollcommand=missing_scrollbar.set)

        # Layout: Treeview on left, scrollbar on right
        #self.records_tree.grid(row=0, column=0, sticky="nse")
        missing_scrollbar.grid(row=1, column=1, sticky="ns")
        
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
    
    def display_popup_yes_no(self,title:str,message:str,detail:str) -> bool:
        return messagebox.askyesno(title=title, message=message,detail=detail)

    def jump_to_barcode(self,barcode:str)->None:
        """move the treeview to the position of the barcode"""
        iid = self.iid_to_barcode_map[barcode]
        self.records_tree.see(iid)
    def highlight_barcode(self,barcode:str)->None:
        """ Highlight the barcode in the treeview"""
        self.records_tree.selection_set(self.iid_to_barcode_map[barcode])

    def setTitle(self,title:str) ->None:
        """Set the main window title"""
        self.title(title)