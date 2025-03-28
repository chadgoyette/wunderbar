# wunderbar
Wunderbar Ice Shaver Controller

This Repo will cover the firmware used to run the wunderbar ice shaver controller

Hardware:
-Raspberry Pi 4
-ELECROW 5 inch Monitor https://www.amazon.com/dp/B07FDYXPT7?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2 
-05 kg Load cell with HX711 https://www.amazon.com/dp/B09VYSHW16?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1&th=1
-Motor Controller: MC-BLDC-300-S -https://drive.google.com/file/d/1VLRH94CGz9MH8I4JuhrhPnIT11xdECwr/view
-Motor: BLDC-J57-107-36-4800-04 


Pin connections to pi:
HX711 - Pin SCK->GPIO-17
      - Pin DO->GPIO-18
MLDC Motor Driver
      ----2 Pin Harness-------
      {-Pin SV->GPIO-5 (Yellow)
       -GND (Black)
      }
      ------5 Pin Harness----------
      {-Pin EN->GPIO-20 (Red)       Low to run
      -Pin BRK->GPIO-19 (Yellow)    Low to run
      -Pin Speed->GPIO-16 (Green)   Speed = pulse frequency output from motor controller for speed feedback. N(rpm)=(F/P)x60/3      F=frequency, P = motor pole pairs (4), N = motor speed
      -Pin ALM->GPIO-13 (White)     High= normal, LOW= Fault
      -PIN XX->GPIO-12 (Blue)       Direction Control
      }
Lid Interlock Switch 
      ----2 Pin Harness ------------
      -Pin GPIO-25 (Blue)
      -GND (Blue)


source ~/hx711_env/bin/activate
export DISPLAY=:0
python ui.py
know good calibration: {"offset": 527965.5, "A": 0.0023111395723669553, "B": 0.3196233805473696}