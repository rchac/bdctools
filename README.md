# bdctools
Tools for ISPs to generate Broadband Data Collection (BDC) reports. Assumes UISP as CRM.

## How it works
bdcAvailability.py pulls in known eligible addresses from eligible.csv, and checks each address against an overlay map (Service Area.kml) to see what the max plan speed offered at that address is. It then checks FCC_Active.csv (the CostQuest Broadband Fabric file) to see if that address can be matched with one in the fabric. If so, it adds that location_id to a list with its corresponding max bandwidth offered, and outputs bdcAvailability.csv.

bdcSubscription.py pulls in a list of UISP crm clients (ucrm.csv), and checks each address against a KML overlay map (Service Area.kml) to see what the max plan speed offered at that address is. It tallies commercial and residential subscribers - using Companyname as the indicator of business vs residential. Then it outputs bdcSubscription.csv.

## Required files
- eligible.csv
- ucrm.csv
- Service Area.kml
- FCC_Active.csv

## Required pip modules
```python3 -m pip install folium censusgeocode shapely gdal```

### eligible.csv
A list of locations eligible for your service, which you have verified using LIDAR and RF propogation models. Template available in files. Business Name, First Name, and Last Name are not required.

If you don't already have a list of known locations, you can use [Google Network Planner](https://wirelessconnectivity.google.com/networkplanner/welcome), [cnHeat](https://cnheat.cambiumnetworks.com/) or [TowerCoverage](https://www.towercoverage.com/) to generate a preliminary list of eligible addresses, which you can then refine and correct. No matter how much you trust any RF Propogation modeling software, you should manually verify each address to ensure eligibility using multiple methods. These eligible addresses must be precise and accurate, not best guesses.

### ucrm.csv
To obtain this, go to UISP CRM > Clients > Active Clients > Select All > Select all X items > Export with Services. UISP CRM Plan names must be formatted as:
```Plan Area | 25/5 Mbps Home Internet```
It will look for '|' and ' Mbps', taking the 25 to be the plan download and 5 to be the plan upload. Alternatively you can hardcode or change the code to use other identifiers to determine plan speed.

If Companyname is empty, it will be assumed to be residential service.

### Service Area.kml
To obtain this, create a Google Maps custom map following the formatting of [this template](https://www.google.com/maps/d/u/0/edit?mid=1-468H_snEfzXTjrnuyBU2OQs0Odaf8E&usp=sharing). There should be one layer, titled 'Service Area' with plan speeds listed in the format of 'Up to X/Y Mbps' where X is download speed and Y is upload speed. Once you have your map created with all eligible areas covered - click the 3-dot options button to the right of Service Area. Then select Export Data > KML. Choose "Export as KML instead of KMZ. Does not support all icons."

### FCC_Active.csv
Learn more [here](https://help.bdc.fcc.gov/hc/en-us/articles/5377509232283-How-Fixed-Broadband-Service-Providers-Can-Access-the-Location-Fabric).
