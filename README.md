# bdctools
Tools for ISPs to generate Broadband Data Collection (BDC) reports.

## Required files
- eligible.csv
- ucrm.csv
- Service Area.kml
- FCC_Active.csv

### eligible.csv
A list of locations eligible for your service, which you have verified using LIDAR and RF propogation models. Fields:
- Business Name (optional)
- First Name (optional)
- Last Name (optional)
- Address
- City
- State
- Zip
- Latitude
- Longitude

### ucrm.csv
To obtain this, go to UISP CRM > Clients > Active Clients > Select All > Select all X items > Export with Services. UISP CRM Plan names must be formatted as:
```Plan Area | 25/5 Mbps Home Internet```
It will look for '|' and ' Mbps', taking the 25 to be the plan download and 5 to be the plan upload. Alternatively you can hardcode or change the code to use other identifiers to determine plan speed.

### Service Area.kml
To obtain this, create a Google Maps custom map following the formatting of [this template](https://www.google.com/maps/d/u/0/edit?mid=1-468H_snEfzXTjrnuyBU2OQs0Odaf8E&usp=sharing). There should be one layer, titled 'Service Area' with plan speeds listed in the format of 'Up to X/Y Mbps' where X is download speed and Y is upload speed. Once you have your map created with all eligible areas covered - click the 3-dot options button to the right of Service Area. Then select Export Data > KML. Choose "Export as KML instead of KMZ. Does not support all icons."

### FCC_Active.csv
Learn more [here](https://help.bdc.fcc.gov/hc/en-us/articles/5377509232283-How-Fixed-Broadband-Service-Providers-Can-Access-the-Location-Fabric).
