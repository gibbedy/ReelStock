from tkinter import Tk,PhotoImage,Frame,Button,Text,messagebox,Toplevel,Label,NORMAL,END,INSERT,DISABLED,Event,Entry,TclError,Widget,BooleanVar,Checkbutton
from typing import Any,Callable,Protocol
from tkinter.filedialog import askopenfilename,asksaveasfilename
from tkinter.ttk import Treeview,Scrollbar,Style
from fileAccess_model import resource_path

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
    def handle_copy_unknown_btn(self):
        ...
    def handle_copy_missing_btn(self):
        ...
    def handle_pretend_found(self,barcode:str):
        ...
    def handle_presenter_btn(self,barcode:str):
        ...
    def handle_manual_entry(self,barcode:str):
        ...
    def handle_start_new_btn(self):
        ...
    def continue_existing_btn(self):
        ...
    def handle_voice_enabled_checkbutton(self):
        ...
    def search_by_filter(self):
        ...

class Tk_view(Tk):
    def __init__(self,test_scan_enabled = False)->None:
        super().__init__()
        self.title("Reel Stocktake")
        scanIcon=PhotoImage(file=resource_path("assets/icons/Zebra64.png"))
        self.iconphoto(True,scanIcon)
        self._maximize_windows()
        self.style = Style(self)

        # Create or configure a style for Treeview
        self.style.configure("Treeview", font=("TkDefaultFont", 14))         # table text
        self.style.configure("Treeview.Heading", font=("TkDefaultFont", 16,"bold")) # header text

        self.section_font = ("TkDefaultFont", 16,"bold")
        self.section_pady = (2,2)
        self.rowconfigure(1, weight=1)      # the row where recordsFrame lives
        self.columnconfigure(0, weight=1)   # the only column

        #File data text color is assigned to these tags
        self.group_color_tags = [("dataID_1",),
                ("dataID_2",),
                ("dataID_3",),
                ("dataID_4",),
                ("dataID_5",),
                ("dataID_6",),
                ("dataID_7",),
                ("dataID_8",),
                ]
        self.test_scan_enabled = test_scan_enabled
        self.presenter:Presenter = None
     
    def close(self):
        """close the applicaiton windows"""
        self.destroy()

    def _maximize_windows(self):
        try:
                self.state('zoomed') #only works in windows. 
                return
        except TclError:
                pass
        try:
                self.attributes('-zoomed',True) #Works in X11
                return
        except TclError:
                pass #Give up here

    def old_maximize_windows(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+0+0')

    def mode_selection_window(self,presenter:Presenter):
        whole_frame = Frame(master=self,bg="white")
        whole_frame.grid()
        whole_frame.grid_rowconfigure(0,weight=1)
        whole_frame.grid_columnconfigure(0,weight=1)
    

        title = Label(master=whole_frame,text="Starting a new stocktake, or continuing an existing stocktake?")
        title.grid(row=0,column=0)

        start_new_btn = Button(master=whole_frame,text="Start New Stocktake",command=presenter.handle_start_new_btn)
        start_new_btn.grid(row=1,column=0)

        continue_existing_btn = Button(master=whole_frame,text="Continue Existing Stocktake",command=presenter.continue_existing_btn)
        continue_existing_btn.grid(row=1,column=1)
      
    def show_help(self,message:str):
        """ put a message in a Text box
        textbox: the Text box object that you want to put the message in
        message: the string to put in the text box"""
        self.infoTextBox.config(state=NORMAL)  # text box is probably disabled to prevent input before this command was given
        self.infoTextBox.delete("1.0",END) #clear the textbox
        self.infoTextBox.insert(INSERT,message)
        self.infoTextBox.config(state=DISABLED)

    def append_message(self,message:str):
        """ put a message in the message textbox
        message: the string to put in the text box"""
        self.messageTextBox.config(state=NORMAL)  # text box is probably disabled to prevent input before this command was given
        #self.messageTextBox.delete("1.0",END) #clear the textbox
        self.messageTextBox.insert("1.0",message+'\n')
        self.messageTextBox.config(state=DISABLED)

    def set_help(self,widgets:Button,hlp_message:str):
            """ assign help text for a givent widget to a the info text box.
                aButton: A reference to a ttk.Button (will work for any widget that supports bind) that you want to have a tooltip for
                hlp_message: A string of text that will appear in the help textbox"""    
            if not isinstance(widgets,(list,tuple,set)):
                widgets = [widgets] 
            for widget in widgets:
                widget.bind("<Enter>", lambda e: self.show_help(hlp_message))
                widget.bind("<Leave>", lambda e: self.clear_help())

    def clear_help(self):
        self.show_help("")
    def alert_bell(self):
        """ Plays an audible alert tone"""
        self.bell()
        return   
    """Functions that must be implemented for the  presenter"""

    def _create_ui_top_level_gui_frames(self):
        frame_borderwidth=1
        frame_relief="solid" #"flat" #"groove"
        #Menu bar across the top of the window. Frame is full window width
        self.menuFrame = Frame(master=self,borderwidth=frame_borderwidth,relief=frame_relief)
        self.menuFrame.grid(row=0, sticky="ew")     

        #Main frame that holds the record data on the left and the file info/legend etc on the right.
        self.mainFrame = Frame(master=self,relief="solid",borderwidth="1")
        self.mainFrame.columnconfigure(0,minsize=815) # column 0 of this frame will have a minimum width of 815 pixels and will expand to fill all available horizontal space
        self.mainFrame.columnconfigure(2,weight=1)
        self.mainFrame.rowconfigure(1,weight=1) # row 1 in the mainFrame will expand to whatever height is available.
        self.mainFrame.grid(row=1,column=0,sticky="nswe")   #sticky here makes the mainframe expand to fill the parent cell (row 1 col 0)


        #Records frame to hold treeview of data and scrollbar (needs two columns)
        self.recordsFrame = Frame(master=self.mainFrame,relief="solid",borderwidth=1)
        self.recordsFrame.grid(row=0, column=0, rowspan=2,sticky="nsew",padx=5, pady=(0,5))
        self.recordsFrame.columnconfigure(0,weight=1)

        self.fileLegendFrame = Frame(master=self.mainFrame,relief="solid",borderwidth=1)
        self.fileLegendFrame.grid(row=0,column=2,sticky="nsew")
        self.fileLegendFrame.columnconfigure(0,weight=1)

        self.manualUtilitiesFrame = Frame(master=self.mainFrame,relief="solid",borderwidth=1)
        self.manualUtilitiesFrame.grid(row=1,column=2,sticky="nsew")
        self.manualUtilitiesFrame.columnconfigure(1,weight=1)
        

    def _create_ui_menu_widgets(self,presenter:Presenter):
        
         #menuFrame widgets:

        self.infoTextBox = Text(master=self.menuFrame,width=100,height=8)
        self.infoTextBox.grid(row=0,column=0,padx=5)
        startupInfo = ("1 - Export Reel stock information from SAP as an Excel spreadsheet\n" +
                        "2 - Drag this file onto the 'Reelstock' icon on the desktop\n" +
                        "    Reel data will be loaded from the spreadsheet and grouped by 'Material' and 'Batch width'\n" +
                        "3 - Plug in the Zebra DS3678-XR barcode scanner base and scan reel barcodes\n" +
                        "    - Scanned barcodes will change color to green\n"
                        "    - Unknown barcodes will be inserted and appear as orange\n"+
                        "5 - Press 'Stocktake Report' button to show missed and unknown reels")

        self.infoTextBox.insert("1.0",startupInfo)
        self.set_help(self.infoTextBox,startupInfo)

        menuPadx=3
        sample_x = 8
        sample_y = 8

        self.testButtonImg = PhotoImage(file=resource_path("assets/icons/Ai_Scan_Barcode.png")).subsample(sample_x,sample_y)
        self.loadButtonImg = PhotoImage(file=resource_path("assets/icons/Ai_Load_Reel_Data.png")).subsample(sample_x,sample_y)
        self.reportButtonImg = PhotoImage(file=resource_path("assets/icons/Ai_Stocktake_Report.png")).subsample(sample_x,sample_y)
        self.hideButtonImg = PhotoImage(file=resource_path("assets/icons/Ai_Hide_Found_Reels.png")).subsample(int(sample_x),int(sample_y))
        self.showButtonImg = PhotoImage(file=resource_path("assets/icons/Ai_Show_Found_Reels.png")).subsample(int(sample_x),int(sample_y))
        self.saveProgressImg = PhotoImage(file=resource_path("assets/icons/Ai_Save_Progress.png")).subsample(int(sample_x),int(sample_y))
        self.loadStocktakeImg = PhotoImage(file=resource_path("assets/icons/Ai_Load_Test.png")).subsample(int(sample_x),int(sample_y))

        self.loadButton = Button(master=self.menuFrame,text="Load",command=presenter.handle_load_btn, image=self.loadButtonImg)
        #self.loadButton.grid(row=0,column=1,padx=menuPadx)
        self.set_help(self.loadButton,"Opens an Excel spreadsheet file.\n" +
                            "If there is already reel data loaded from a previous load, a dialog box will come up asking if you want to append or overwrite the data.\n" +
                            "This will allow loading of multiple seperate spreadsheets which is something Jan says is required")

        self.reportButton = Button(master=self.menuFrame,text="Show Report",command=presenter.handle_report_btn, image=self.reportButtonImg)
        self.reportButton.grid(row=0,rowspan=2,column=2,padx=menuPadx)
        self.set_help(self.reportButton,"Create a report showing missing reels and unknown reels.")

        self.hideButton = Button(master=self.menuFrame,text="Hide Found Reels",command=presenter.handle_hide_btn,image=self.hideButtonImg)
        self.hideButton.grid(row=0,column=3,padx=menuPadx)
        self.set_help(self.hideButton,"Hide any reels that have already been scanned")

        self.showButton = Button(master=self.menuFrame,text="Show Found Reels",command=presenter.handle_show_btn, image=self.showButtonImg)
        self.showButton.grid(row=0,column=4,padx=menuPadx)
        self.set_help(self.showButton,"Show all reels if they have been hidden with hide reels")

        self.testButton = Button(master=self.menuFrame,text="Random Barcod Scan Simulation Button",command=presenter.handle_test_btn,image=self.testButtonImg)
        if self.test_scan_enabled:
            self.testButton.grid(row=0, column=5,padx=menuPadx)
            
        self.set_help(self.testButton,"This button simulates a scann of a random barcode from the data\n" +
            "Simulator will randomly scan a barcode that is not in the database to simulate finding a new Reel.\n" +
            "Found items will be highlighted in green, new reels found will be highlighted in orange at the end of the list"
            "This button will be removed when we have the scanner hardware")
        
        self.saveProgressButton = Button(master=self.menuFrame,text="Save Progress",command=presenter.handle_save_btn,image=self.saveProgressImg)
        #self.saveProgressButton.grid(row=0, column=6,padx=menuPadx)
        self.set_help(self.saveProgressButton,"Save the current stocktake results so it can be continued at a later time.")

        #self.loadStocktakeButton = Button(master=self.menuFrame,text="Save Progress",command=presenter.handle_load_stocktake_btn,image=self.loadStocktakeImg)
        #self.loadStocktakeButton.grid(row=1, column=6,padx=menuPadx)
        #self.set_help(self.loadStocktakeButton,"Load a previously saved stocktake.")

        #Voice enable/dissable
        self.voice_enabled = BooleanVar(value=True)
        self.voice_enabled_checkbutton = Checkbutton(master=self.menuFrame,text="Enable Voice Alerts",variable=self.voice_enabled,command=presenter.handle_voice_enabled_checkbutton)
        self.voice_enabled_checkbutton.grid(row=0,column=6,padx=menuPadx)
        self.set_help(self.voice_enabled_checkbutton,"Enables or dissables voice alerts like 'found','unknown','duplicate'...")
        #self.voice_enabled.get().. set(True)

    def _create_ui_fileLegendFrame_widgets(self):
        #fileLegendFrame Widgets:
        #...
        self.loaded_files_tree_Frame = Frame(master=self.fileLegendFrame)
        self.loaded_files_tree_Frame.columnconfigure(0,weight=1)
        
        self.loaded_files_tree_Frame.grid(row=0,column=0,sticky="we")
        loaded_files_title = Label(master=self.loaded_files_tree_Frame,text="Sap Stocktake Data files that have been loaded",font=self.section_font)
        loaded_files_title.grid(row=0,column=0,pady=self.section_pady)

        self.loaded_files_tree = Treeview(master=self.loaded_files_tree_Frame,columns=("File Number","File Path"),show="headings",height=3)
        self._set_group_tag_text_colors(self.loaded_files_tree)
        self.loaded_files_tree.grid(row=1,column=0,sticky="nsew")
        self.loaded_files_tree.column('File Number',width=50,stretch=False)
        self.loaded_files_tree.column('File Path',width=700,stretch=True)
        self.loaded_files_tree.heading('File Number', text='ID',anchor="w")
        self.loaded_files_tree.heading('File Path', text='File Path',anchor="w")

        self.set_help(self.loaded_files_tree,"Excel reel inventory files will be listed here after they are loaded.\n" +
            "The text color here will match the reel data text color.")
        
        self.messageFrame = Frame(master=self.fileLegendFrame)
        self.messageFrame.grid(row=2,column=0,sticky="nsew")
        self.messageFrame.columnconfigure(0,weight=1)

        self.set_help(self.messageFrame,"Status updates like when a duplicate barcode is scanned are updated here" +
                                        "\n The most recent status message will be on the top")

        Label(master=self.messageFrame,font=self.section_font,text="Errors and Information Log").grid(row=0,column=0,pady=self.section_pady)
        self.messageTextBox = Text(master=self.messageFrame,height=30)
        self.messageTextBox.grid(row=1,column=0,sticky="ew")
        self.messageTextBox.config(state=DISABLED)
              
    def create_ui(self,presenter:Presenter):
        """Creates all components of the tkinter user interface"""
        self.presenter = presenter
        self._create_ui_top_level_gui_frames()   
        # Or explicitly for all Labels only
        self.option_add("*Label.Font", ("TkDefaultFont", 13))
        
        self._create_ui_menu_widgets(presenter=presenter)
        self._create_ui_fileLegendFrame_widgets()
        self._manual_entry_gui() 
        self.create_ui_reel_search()
        self.capture_scanner()

    def _manual_entry_gui(self):
        """Gui elements for manual barcode entry"""
        self.keyboardEntryFrame = Frame(master=self.manualUtilitiesFrame,relief='solid',borderwidth=1)
        self.keyboardEntryFrame.grid(row=0,column=0,padx=1,pady=1,sticky="we")
        self.keyboardEntryFrame.columnconfigure(1,weight=1)

        self.set_help(self.keyboardEntryFrame,"Manually input a barcode here and hit the update button to add any barcodes that can't be scanned")

        manual_entry_heading = Label(master=self.keyboardEntryFrame,text="Manual Barcode Entry",font=self.section_font)
        manual_entry_heading.grid(row=0,column=0,columnspan=3,pady=self.section_pady)
        self.set_help(manual_entry_heading,"Manually input a barcode here and hit the update button to add any barcodes that can't be scanned")

        self.entryLabel = Label(master=self.keyboardEntryFrame,text="Barcode:")
        self.entryLabel.grid(row=1,column=0,sticky="new")
        self.set_help(self.entryLabel,"Manually input a barcode here and hit the update button to add any barcodes that can't be scanned")

        self.entryTextBox = Entry(master=self.keyboardEntryFrame,width=30,font=("Helvetica", "16"))
        self.entryTextBox.grid(row=1,column=1,sticky="new")
        self.entryTextBox.config(state=NORMAL)
        self.set_help(self.entryTextBox,"Manually input a barcode here and hit the update button to add any barcodes that can't be scanned")

        self.entryUpdate = Button(master = self.keyboardEntryFrame,text="Update",command=self.handle_entry)
        self.entryUpdate.grid(row=1,column=2,sticky="nwe")

    def create_ui_reel_search(self):
        search_widgets = []
        #Main frame for search
        self.reelSearchFrame = Frame(master=self.manualUtilitiesFrame,relief='solid',borderwidth=1)
        self.reelSearchFrame.grid(row=1,column=0,padx=1,pady=1,sticky='w')
        #self.reelSearchFrame.columnconfigure(0,weight=1)
        #self.reelSearchFrame.columnconfigure(1,weight=1)
        #self.reelSearchFrame.columnconfigure(2,weight=1)

        search_widgets.append(self.reelSearchFrame)

        barcode_search_title = Label(master=self.reelSearchFrame,text="Find Reels With Incompolete Barcode", font=self.section_font)
        barcode_search_title.grid(row=0,column=0,columnspan=3,pady=self.section_pady)
        
        search_widgets.append(barcode_search_title
                           )
        digits_padx=10

        #Frame for barcode characters portion of search
        barcodeCharactersFrame = Frame(master=self.reelSearchFrame,relief='solid',borderwidth=0)
        barcodeCharactersFrame.grid(row=1,column=0,padx=digits_padx)
        search_widgets.append(barcodeCharactersFrame)

        #Frame for weight digits portion of search
        weightDigitsFrame = Frame(master=self.reelSearchFrame,relief='solid',borderwidth=0)
        weightDigitsFrame.grid(row=1,column=1,padx=digits_padx)
        search_widgets.append(weightDigitsFrame)

        #Frame for width digits portion of search
        widthDigitsFrame = Frame(master=self.reelSearchFrame,relief='solid',borderwidth=0)
        widthDigitsFrame.grid(row=1,column=2,padx=digits_padx)
        search_widgets.append(widthDigitsFrame)

        #Barcode Characters search heading
        search_widgets.append(Label(master=barcodeCharactersFrame,text="Barcode Characters"))
        search_widgets[-1].grid(row=0,column=0)

        #Width Digits search heading
        search_widgets.append(Label(master=widthDigitsFrame,text="Width Digits"))
        search_widgets[-1].grid(row=0,column=0)

        #Barcode Characters search heading
        search_widgets.append(Label(master=weightDigitsFrame,text="Weight Digits"))
        search_widgets[-1].grid(row=0,column=0)

        #Frame for Barcode character and entry boxes
        b_digit_entry_Frame  = Frame(master=barcodeCharactersFrame,relief='solid',borderwidth=0)
        b_digit_entry_Frame.grid(row=1,column=0)
        search_widgets.append(b_digit_entry_Frame)
    

        #Frame for weight digit and entry boxes
        weight_digit_entry_Frame = Frame(master=weightDigitsFrame,relief='solid',borderwidth=0)
        weight_digit_entry_Frame.grid(row=1,column=0)
        search_widgets.append(weight_digit_entry_Frame)

        #Frame for width digit and entry boxes
        width_digit_entry_Frame = Frame(master=widthDigitsFrame,relief='solid',borderwidth=0)
        width_digit_entry_Frame.grid(row=1,column=0)
        search_widgets.append(width_digit_entry_Frame)

        digit_entry_width = 5
        digit_entry_height = 5
        #barcode filter labels and entry boxes
        self.search_filter_barcode:list[Entry] = []
        for digit in range(1,11):
            search_widgets.append(Label(master=b_digit_entry_Frame,text=str(digit)))
            search_widgets[-1].grid(row=0,column=digit) 
            self.search_filter_barcode.append(Entry(master=b_digit_entry_Frame,width=digit_entry_width))
            self.search_filter_barcode[digit-1].grid(row=1,column=digit)
            self.search_filter_barcode[digit-1].bind("<Key>",self.reel_search_entry_process)
            self.prioritise_all_tag_for_widget(self.search_filter_barcode[digit-1])
            search_widgets.append(self.search_filter_barcode[digit-1])

        #width filter labels and entry boxes
        self.search_filter_width:list[Entry] = []
        for digit in range(1,5):
            search_widgets.append(Label(master=width_digit_entry_Frame,text=str(digit)))
            search_widgets[-1].grid(row=0,column=digit)
            self.search_filter_width.append(Entry(master=width_digit_entry_Frame,width=digit_entry_width))
            self.search_filter_width[digit-1].grid(row=1,column=digit)
            self.search_filter_width[digit-1].bind("<Key>",self.reel_search_entry_process)
            self.prioritise_all_tag_for_widget(self.search_filter_width[digit-1])
            search_widgets.append(self.search_filter_width[digit-1])

        #weight filter labels and entry boxes
        self.search_filter_weight:list[Entry] = []
        for digit in range(1,5):
            search_widgets.append(Label(master=weight_digit_entry_Frame,text=str(digit)))
            search_widgets[-1].grid(row=0,column=digit)
            self.search_filter_weight.append(Entry(master=weight_digit_entry_Frame,width=digit_entry_width))
            self.search_filter_weight[digit-1].grid(row=1,column=digit)
            self.search_filter_weight[digit-1].bind("<Key>",self.reel_search_entry_process)
            self.prioritise_all_tag_for_widget(self.search_filter_weight[digit-1])
            search_widgets.append(self.search_filter_weight[digit-1])

        self.set_help(search_widgets,"Search for reels based on whatever limited information you can read from the reel")

        def check_digitFrame_entry():
            ...
    def reel_search_entry_process(self,event:Event):
        """single didgit entry boxes bind key events to this function so only one character can
            be inserted into an entry box at a time"""
        w:Entry = event.widget
        
        #special case for barcode start of scan characters. 
        #in this case let the key go through so it can be recieved by the all keybind and 
        #focus can be automatically shifted 
        if event.keysym in ("F13","XF86Tools"): 
            return
        
        #allow tab to move to the next box
        if event.keysym == "Tab":
            w.tk_focusNext().focus()
            return "break"
        
        #allow backspace to clear the entry box
        if event.keysym == "BackSpace":
            w.delete(first=0,last="end")
            self.presenter.search_by_filter()
            
        #ignore non character keys
        if not event.char.isalnum():
            return "break"

        #Everything else:
        # clear the entry box
        w.delete(first=0,last="end")
        #insert the single character as uppercase
        w.insert(0,event.char.upper())
        self.presenter.search_by_filter()

        return "break"


    def get_search_filter_barcode(self):
        barcode_filter = []
        entries:Entry
        for entries in self.search_filter_barcode:
            barcode_filter.append(entries.get())

        return barcode_filter
    
    def get_search_filter_width(self):
        width_filter = []
        entries:Entry
        for entries in self.search_filter_width:
            width_filter.append(entries.get())

        return width_filter
    
    def get_search_filter_weight(self):
        weight_filter = []
        entries:Entry
        for entries in self.search_filter_weight:
            weight_filter.append(entries.get())

        return weight_filter
    
    def handle_entry(self):
        barcode = self.entryTextBox.get()
        self.presenter.handle_manual_entry(barcode)
        self.entryTextBox.delete(0, 'end')

    def on_ctrl_space(self,event:Event):
        #print("control-space was handled")
        selected_items = self.records_tree.selection()
        #print(f'selected items = {selected_items}')
        if selected_items:
            for item in selected_items:
                barcode = self.records_tree.item(item, "values")[0]
                #print(f'barcode should be: {barcode}')
                self.presenter.handle_pretend_found(barcode = barcode)   
        return "break"
    
    def prioritise_all_tag_for_widget(self,w:Widget):
            """This function will change the all tag binding from last place to first place for a given widget.
                This is done so that my function that captures keyboard input (on_key) can be bound to all and decide wether to 
                pass the keystroke onto lower level widgets or not. 
                Currently i'm using it to filter keystrokes going to the manual entry widget so scans can still occur if the focus is currenlty on the manual entry widget"""
            tags = list(w.bindtags())
            if "all" in tags:
                tags.remove("all")
            tags.insert(1,"all")
            w.bindtags(tuple(tags))

    def capture_scanner(self):
        """ Setup how this view will detect a scanner event.
            I'm thinking listening for a code followed by a carriage return on the keyboard"""    

        
        
        #Add prioritise "all" tag for widgets that need keyboard input that I want control over barcode or keyboard entry to
        self.prioritise_all_tag_for_widget(self.entryTextBox) 

        self.scanner_buffer = []

        def on_key(event:Event):
            #print(f'event.keycode={event.keycode}, \nevent.keysym={event.keysym}, \nevent.keysym_num={event.keysym_num},\nevent.char={event.char},\nevent.num={event.num}\n\n')
            widget_with_current_focus = self.focus_get()

            #print(f'key {event.keycode} seen by { self.focus_get()}')

            #Barcode scanner is setup to send a prefix of f13 and suffix of f14
            #Clear anything that may have been put into the keyboard buffer by the user tapping the keyboard
            if event.keysym in ("F13","XF86Tools"):
                self.scanner_buffer.clear() 
                #no matter where i am, if the barcode scans (sending a string of characters starting with the "f13" prefix), put focus on the records treeview. prevents scans being typed into manual entry widgets like the manual barcode entry field.              
                self.records_tree.focus_force()
                return "break"  #prevents the "f13" character getting to anything that had the focus

            # F14 suffix means the end of the barcode
            elif event.keysym in ("F14", "XF86Launch5"):   
                code = "".join(self.scanner_buffer).strip()
                self.scanner_buffer.clear()
                if code:
                    self.presenter.handle_scanner_code(code)  
            else:
                # Ignore modifier keys, arrows, etc.
                if len(event.char) == 1 and event.char.isprintable():
                    self.scanner_buffer.append(event.char)

        # Bind at the application (root) level
        self.bind_all("<Key>", on_key) 

        return None

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
        report_window.transient(self)
        report_window.title(f'Stocktake Report')
        report_window.rowconfigure(0,weight=1,pad=5)
        report_window.columnconfigure(0,weight=1,pad=5)

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
        missing_reels_frame.rowconfigure(1, weight=0)
        missing_reels_frame.columnconfigure(0, weight=0)

        style = Style()
        #style.theme_use("clam")   # clam respects bg colors better
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
        unknown_title.grid(row=0,column=1)
        unknown_title.config(bg=unknown_title.master["bg"])

        unknown_copy_to_clipboard = Button(master=unknown_reels_frame,text="Copy data to clipboard",command=self.presenter.handle_copy_unknown_btn)
        unknown_copy_to_clipboard.grid(row=0,column=0)

        if len(unknown_reels) > 0:
            column_headings = [key for key in unknown_reels[0].keys()]
            unknown_reels_tree = Treeview(master=unknown_reels_frame,columns=column_headings,show="headings")

            unknown_reels_tree.grid(row=1,column=0,padx=10,pady=10,columnspan=3)
            # Create vertical scrollbar
            unknown_scrollbar = Scrollbar(master=unknown_reels_frame, orient="vertical", command=unknown_reels_tree.yview)
            unknown_scrollbar.grid(row=1, column=3, sticky="ns")
            unknown_reels_tree.configure(yscrollcommand=unknown_scrollbar.set)

            for heading in column_headings:
                unknown_reels_tree.heading(heading, text=heading)
                unknown_reels_tree.column(column=heading, stretch=True,minwidth=100)

            for reel in unknown_reels:
                unknown_reels_tree.insert(parent="",index="end",values=list(reel.values()))

        
        missing_title=Label(master=missing_reels_frame,text="Reels not found in the stocktake")
        missing_title.config(bg=missing_title.master["bg"])

        missing_copy_to_clipboard = Button(master=missing_reels_frame,text="Copy data to clipboard", command=self.presenter.handle_copy_missing_btn)
        missing_copy_to_clipboard.grid(row=0,column=0)

        missing_title.grid(row=0,column=1)
        if len(missing_reels) > 0:
            column_headings = [key for key in missing_reels[0].keys()]
            missing_reels_tree = Treeview(master=missing_reels_frame,columns=column_headings,show="headings")
            self._set_group_tag_text_colors(missing_reels_tree)
            missing_reels_tree.grid(row=1,column=0,padx=10,pady=10, sticky="nse",columnspan=3)
            # Create vertical scrollbar
            missing_scrollbar = Scrollbar(master=missing_reels_frame, orient="vertical", command=missing_reels_tree.yview)
            missing_scrollbar.grid(row=1, column=3, sticky="ns")
            missing_reels_tree.configure(yscrollcommand=missing_scrollbar.set)

            for heading in column_headings:
                missing_reels_tree.heading(heading, text=heading)
                missing_reels_tree.column(column=heading, stretch=True,minwidth=100)

            for reel in missing_reels:               
                group_number = list(reel.values())[4]

                if group_number == None or str(group_number).lower()=="none":
                    tags = ()
                else:
                    tags = self.group_color_tags[int(group_number)]

                missing_reels_tree.insert(parent="",index="end",values=list(reel.values()),tags = tags)

        

        # Layout: Treeview on left, scrollbar on right
        #self.records_tree.grid(row=0, column=0, sticky="nse")
    def _set_group_tag_text_colors(self,aTree:Treeview):
        """ create text color tags for a treeview object"""   
        aTree.tag_configure("green", background="lightgreen")
        aTree.tag_configure("orange", background="orange")
        aTree.tag_configure("error", background="red", foreground="white")

        aTree.tag_configure("dataID_1", foreground="black")
        aTree.tag_configure("dataID_2", foreground="red")
        aTree.tag_configure("dataID_3", foreground="yellow")
        aTree.tag_configure("dataID_4", foreground="pink")
        aTree.tag_configure("dataID_5", foreground="green")
        aTree.tag_configure("dataID_6", foreground="purple")
        aTree.tag_configure("dataID_7", foreground="orange")
        aTree.tag_configure("dataID_8", foreground="blue")

    def display_records(self,records:list[list[str]])->None:
        """ Display records in the gui.
            records:list[list[str]] - two dimensional list.. rows of column data"""

        self.iid_to_barcode_map = dict() # Used for mapping treeview rows to the barcode that it contains, so I can toggle colors based on barcodes.
        cols = records[0]
        data = records[1:]

        self.records_tree = Treeview(master=self.recordsFrame,columns=cols,show="headings")
        self.set_help(self.records_tree,"Reel records that have been loaded are displayed here.\n" +
                        "As they are scanned the individual records that are found will be highlighted green.\n" +
                        "Barcodes that have been scanned that are not in the data are highlighted in orange\n" +
                        "Text color is determined by the file which the reeldata has come from\n" +
                        "Click on a record then press 'CTRL + SPACE' to toggle reel as found or not found\n" + 
                        "If toggling is done on an orange unkown reel then it will delete that reel from the records")
        self._set_group_tag_text_colors(self.records_tree)
        self.records_tree.bind("<Control-space>", self.on_ctrl_space)
        
   
        for col in cols:
            self.records_tree.heading(col, text=col,anchor="w")
            self.records_tree.column(col, stretch=True,anchor="w")  # ensure columns expand

        # Insert data rows
        for row in data:
            group_number = row[-1]
            
            #print(f'group number is {group_number}')
            if group_number == None or str(group_number).lower()=="none":
                tags = ()
            else:
                tags = self.group_color_tags[int(group_number)]

            iid = self.records_tree.insert("", "end", values=row,tags=tags) #last column in row is the group number and is not displayed in the treeview but is used here to set text color for different files data
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
      
    def set_file_legend(self,fileID:dict[int,str]):
        """clears and repoplulates the file id/filepath legend treeview widget"""
        self.loaded_files_tree.delete(*self.loaded_files_tree.get_children())
        for index in range(0,len(fileID)):
            iid = self.loaded_files_tree.insert("", "end", values=(index,fileID[index]),tags=self.group_color_tags[index])

    def unknown_reel_found(self,barcode:str):
        """ Insert an unkown reel into the table and mark it orange
            barcode:str - barcode of the reel to be inserted"""
        if barcode not in self.iid_to_barcode_map.keys():      
            self.iid_to_barcode_map[barcode] = self.records_tree.insert("", "end", values=[barcode,"","",""],tags=())
        iid = self.iid_to_barcode_map[barcode]
        #self.records_tree.item(iid, tags="orange",)

        tags = self.records_tree.item(iid, 'tags') or ()
        if isinstance(tags, str):
            tags = (tags,)
        self.records_tree.item(iid, tags=tags + ("orange",))

    def known_reel_found(self,barcode:str):
        """ Mark reel in the table green"""
        iid = self.iid_to_barcode_map[barcode]  
        tags = self.records_tree.item(iid, 'tags') or ()
        if isinstance(tags, str):
            tags = (tags,)
        
        #self.records_tree.item(iid, tags="green",)
        self.records_tree.item(iid, tags=self.records_tree.item(iid,'tags') + ("green",))

    def clear_found(self,barcode:str):
        """Remove colored background for record in records tree"""  
        iid = self.iid_to_barcode_map[barcode]
        tags:tuple = self.records_tree.item(iid,'tags') or ()
        #print(f'tags for {barcode} is {tags}')
        tags = tuple(tag for tag in tags if tag != 'green')
        #print(f'tags after removal of orange and gree for {barcode} is {tags}')
        if isinstance(tags, str):
            tags = (tags,)   
        #self.records_tree.item(iid, tags="green",)
        self.records_tree.item(iid, tags=tags)
    
    def delete_record(self,barcode:str):
        iid = self.iid_to_barcode_map[barcode]
        self.records_tree.delete(iid)
        self.iid_to_barcode_map.pop(barcode)


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

    def copy_lines_to_clipboard(self,lines:list[str]):
        """ Copy lines of text to the clipboard
            lines:list[str] - a list of strings to copy to the clipboard."""
        
        #txt = "\n".join("\t".join(str(x) for x in row) for row in lines)
        txt = lines
        self.clipboard_clear()
        self.clipboard_append(txt)
        self.update()
    
    def is_voice_enabled(self):
        return self.voice_enabled.get()
    
