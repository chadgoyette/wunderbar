#!/bin/bash
cd /home/admin/wunderbar
source /home/admin/hx711_env/bin/activate

# Ensure the correct Qt platform theme and style are applied
export QT_QPA_PLATFORMTHEME=gtk2
export QT_STYLE_OVERRIDE=Fusion

# Ensure the application uses the correct display environment
export DISPLAY=:0

python3 main_ui.py
