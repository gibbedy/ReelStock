source .venv/bin/activate
pyinstaller 
--noconfirm 
--clean 
--name ReelStock 
--add-data "assets/icons:assets/icons" 
--add-data "assets/images:assets/images" 
--add-data "assets/sounds:assets/sounds"
--icon=assets/icons/Zebra64.ico main.py