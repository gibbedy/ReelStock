source .venv/bin/activate 

#!/usr/bin/env bash
set -e

pyinstaller \
--noconfirm \
--clean \
--name ReelStock \
--add-data "assets/icons:assets/icons" \
--add-data "assets/images:assets/images" \
--add-data "assets/sounds:assets/sounds" \
--icon=assets/icons/Zebra64.ico main.py 