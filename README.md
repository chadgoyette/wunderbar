# wunderbar
Wunderbar Ice Shaver Controller

This Repo will cover the firmware used to run the wunderbar ice shaver controller

Hardware:
-Raspberry Pi 4
-ELECROW 5 inch Monitor https://www.amazon.com/dp/B07FDYXPT7?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2 
-05 kg Load cell with HX711 https://www.amazon.com/dp/B09VYSHW16?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1&th=1
-Motor Controller: MC-BLDC-300-S
-Motor: BLDC-J57-107-36-4800-04 


Pin connections to pi:
HX711 - Pin SCK->GPIO-17
      - Pin DO->GPIO-18
MLDC Motor Driver
      -Pin SV->GPIO-5
