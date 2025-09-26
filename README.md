# ReelStock
Python application to perform a stocktake of reels of paper using a barcode scanner.

## Overview
This is a stocktake application to check that actual stock levels of reels of paper match the currently recorded stock levels.
Each 2 tonne reel of paper has a unique barcode. This barcode is scanned by a long range barcode scanner and is recorded as found in the application.
This application was created to speed up the process of performing the stocktake which previously was done using binoculars and manually checking of a printout of the stock records.

##Prerequisites
Developed and tested with python 3.13.1 but should work with any python/OS that support the following libraries:
- tkinter
- pandas
- datetime
- os
- json
- enum
