# ReelStock

Python application to perform a stocktake of reels of paper using a barcode scanner.

## Overview

This is a stocktake application to check that actual stock levels of reels of paper match the currently recorded stock levels from an Excel spreadsheet file.
Each 2 tonne reel of paper has a unique barcode. This barcode is scanned by a long range barcode scanner and is recorded as found by the application.
This application was created to speed up stocktake, which previously was done using binoculars and manually checking a printed list.

## Prerequisites

Developed and tested with Python 3.13.1 on Windows/PC and 3.11.2 on Linux/Raspberry Pi 5.
Libraries required:
- tkinter
- pandas
- datetime
- os
- json
- enum

## Installation
### Using python:
```python main.py```

### Using pyinstaller:

```pyinstaller --noconsole --onefile main.py```

Copy ```assets``` folder (including subfolders) to the same location as the generated ```main.exe```
and run "main.exe"

### Using pre-built PyInstaller executable:

Download zip of assets and pyinstaller executable and ```main.exe```

## Usage:

### Main application Window:
<img src="assets/images/main_window.PNG" width=800>

At the top left of the main window is a text box.  This text box will display help information based on the area the mouse pointer is located. This will be updated to reflect how the current version of the application operates. Below is a general overview of how the application functions.

Current stock levels are loaded as an Excel spreadsheet.  Multiple files can be loaded at once, each files data is separated visually using a different colored text and that legend is displayed on screen.  The column names determine how this data is intereted and is hard coded in the application.
A barcode scanner scans reels in the store which updates this data to show that the reels have been found.  The barcode scanner needs to be setup in USB HID keyboard mode and to append a carriage return to every barcode as it is scanned.
A stocktake test can be saved and loaded as required. As an emergency backup, every barcode scanned is logged by date in a separate text file to minimize the chance that a technical failure can cause a significant time loss.

### Report Window:

<img src="assets/images/report_window.PNG" width=800>

When all reels have been scanned a report can be generated to show what reels were missing as well as any reels found that were not in the stocktake data.
Report data can be copied to the clipboard to update whatever system is used. Currently I have it as tab delimited text.

## Roadmap:

This project is designed to contain everything needed to maintain / update the app in one place, so that anyone can run or extend its cababilities without relying on me personally.

### Planned Additions:

 - Scanner QR code setup image: a button to display the QR codes that are required to setup the Zebra 3738XR barcode scanner.
 - Customize report format or clipboard copy format to most suit how this data is used (I currently don't know the application stocktake data needs to be updated to)
 - Seprate format of stocktake data input into a seperate config file that can be edited seperately so the program can be modified to suit different input formats.

