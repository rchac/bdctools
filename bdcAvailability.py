import csv
from geojson import Feature, FeatureCollection, Point, Polygon
from ipyleaflet import Map, GeoJSON
import folium
import json
from osgeo import gdal, ogr
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry import shape, mapping
from ispSettings import provider_id, brand_name, low_latency, technology, business_residential_code, lowestPlanOfferedMbpsDownload, lowestPlanOfferedMbpsUpload

def pullEligibleAddresses():
	eligibleAddressList = []
	with open('eligible.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				#print('header')
				line_count += 1
			else:
				BusinessName, FirstName, LastName, Address, City, State, Zip, Latitude, Longitude = row
				eligibleAddressList.append((BusinessName, FirstName, LastName, Address, City, State, Zip, Latitude, Longitude, lowestPlanOfferedMbpsDownload, lowestPlanOfferedMbpsUpload))
				line_count += 1
				#print(Address + ' ' + Address2)

	mostRecentUserID = None
	idCompanyName = {}
	idAddress = {}
	with open('ucrm.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					#print(f'Column names are {", ".join(row)}')
					header_store = row
					line_count += 1
				else:
					Id, CustomID, Firstname, Lastname, Name, Username, Companyname, IsLead, Clientlatitude, Clientlongitude, Companyregistrationnumber, CompanytaxID, Clienttaxrate1, Clienttaxrate2, Clienttaxrate3, Companywebsite, Emails, Phones, Address, Balance, Street1, Street2, City, Country, State, ZIPcode, InvoiceStreet1, InvoiceStreet2, InvoiceCity, InvoiceCountry, InvoiceState, InvoiceZIPcode, Invoiceaddresssameascontact, Registrationdate, Note, Archived, Service, Serviceperiod, Serviceindividualprice, Serviceinvoicelabel, Servicelatitude, Servicelongitude, Servicenote, Serviceactivefrom, Serviceactiveto, Serviceinvoicingfrom, Serviceinvoicingtype, Servicecontracttype, Servicecontractenddate, Serviceinvoicingperiodstartday, ServicecreateinvoiceXdaysinadvance, Serviceinvoiceseparately, Serviceinvoiceusecreditautomatically, Serviceminimumcontractlength, Servicesetupfee, Serviceearlyterminationfee, Serviceinvoiceapproveandsendautomatically, LocationID, Servicetax1, Servicetax2, Servicetax3, ServicecontractID, ServiceCensusBlockGEOID, Serviceprepaid = row
					if Id:
						mostRecentUserID = Id
						idCompanyName[Id] = Companyname
						idAddress[Id] = (Street1, City, State, ZIPcode)
					if not Id:
						if '|' in Service:
							planMbpsDown = int(Service.split(' | ')[1].split('/')[0])
							planMbpsUp = int(Service.split(' | ')[1].split('/')[1].split(' Mbps')[0])
						idStreet1, idCity, idState, idZIPcode = idAddress[mostRecentUserID]
						if (Clientlatitude != '') and (Clientlongitude != ''):
							eligibleAddressList.append((idCompanyName[mostRecentUserID], Firstname, Lastname , idStreet1, idCity, idState, idZIPcode, Clientlatitude, Clientlongitude, planMbpsDown, planMbpsUp))
					line_count += 1

	srcDS = gdal.OpenEx('Service Area.kml')
	ds = gdal.VectorTranslate('coverage.geojson', srcDS, format='GeoJSON')
	del ds

	eligibleAddressListWithSpeeds = []

	geo_json_map = json.load(open('coverage.geojson'))
	for salesLead in eligibleAddressList:
		BusinessName, FirstName, LastName, Address, City, State, Zip, Latitude, Longitude, planMbpsDown, planMbpsUp = salesLead
		mbpsDownMax = planMbpsDown
		mbpsUpMax = planMbpsUp
		for item in geo_json_map['features']:
			mbpsDown = int(item['properties']['Name'].split('Up to ')[1].replace(' Mbps','').split('/')[0])
			mbpsUp = int(item['properties']['Name'].split('Up to ')[1].replace(' Mbps','').split('/')[1])
			p1 = Polygon(item['geometry']['coordinates'][0])
			point = Point(float(Longitude), float(Latitude))
			polygon = p1
			if polygon.contains(point):
				if mbpsDown > mbpsDownMax:
					mbpsDownMax = mbpsDown
				if mbpsUp > mbpsUpMax:
					mbpsUpMax = mbpsUp
				
		eligibleAddressListWithSpeeds.append((BusinessName, FirstName, LastName, Address, City, State, Zip, Latitude, Longitude, str(mbpsDownMax), str(mbpsUpMax)))
		
	return eligibleAddressListWithSpeeds

def removeUnits(address):
	address = address.upper()
	if '#' in address:
		address = address.split('#',1)[0]
	if ' UNIT ' in address:
		address = address.split(' UNIT ',1)[0]
	if ' APT ' in address:
		address = address.split(' APT ',1)[0]
	if ' SUITE ' in address:
		address = address.split(' SUITE ',1)[0]
	
	return address

def cleanAddress(inputAddress):
	tmp = inputAddress.upper()
	tmp = tmp + "!"
	tmp = tmp.replace(" DRIVE!", " DR!")
	tmp = tmp.replace(" COURT!", " CT!")
	tmp = tmp.replace(" CIRCLE!", " CIR")
	tmp = tmp.replace(" PLACE!", " PL!")
	tmp = tmp.replace(" LANE!", " LN!")
	tmp = tmp.replace(" AVENUE!", " AVE!")
	tmp = tmp.replace(" ROAD!", " RD!")
	tmp = tmp.replace(" STREET!", " ST!")
	tmp = tmp.replace("!", "")
	tmp = tmp.strip().title()
	return tmp

def strippedAddress(inputAddress):
	tmp = inputAddress.upper()
	tmp = tmp + "!"
	tmp = tmp.replace(" DR!", " !")
	tmp = tmp.replace(" DRIVE!", " !")
	tmp = tmp.replace(" CT!", " !")
	tmp = tmp.replace(" COURT!", " !")
	tmp = tmp.replace(" CIR!", " !")
	tmp = tmp.replace(" CIRCLE!", " !")
	tmp = tmp.replace(" PL!", " !")
	tmp = tmp.replace(" PLACE!", " !")
	tmp = tmp.replace(" LN!", " !")
	tmp = tmp.replace(" LANE!", " !")
	tmp = tmp.replace(" AVE!", " !")
	tmp = tmp.replace(" AVENUE!", " !")
	tmp = tmp.replace(" WAY!", " !")
	tmp = tmp.replace(" RD!", " !")
	tmp = tmp.replace(" ROAD!", " !")
	tmp = tmp.replace(" ST!", " !")
	tmp = tmp.replace(" STREET!", " !")
	tmp = tmp.replace("!", "")
	tmp = tmp.strip().title()
	return tmp

if __name__ == '__main__':
	locationsToSave = []
	eligibleList = []
	addressesOnly = []
	eligibleAddressListWithSpeeds = pullEligibleAddresses()
	
	for entry in eligibleAddressListWithSpeeds:
		BusinessName, FirstName, LastName, Address, City, State, Zip, Latitude, Longitude, MbpsDown, MbpsUp = entry
		unitNum = None
		streetNum = None
		streetName = None
		bldg = None
		Address = Address.upper().strip()
		City = City.upper().strip()
		State = State.upper().strip()
		Zip = Zip.strip()
		thisAddress = removeUnits(Address)
		thisAddress = cleanAddress(thisAddress)
		if thisAddress not in addressesOnly:
			addressesOnly.append(strippedAddress(thisAddress))
			eligibleList.append((thisAddress, City, State, Zip, MbpsDown, MbpsUp))
	print(str(len(eligibleAddressListWithSpeeds)) + " eligible locations imported from file.")
	
	print("Attempting to match locations to Broadband Fabric Locations")
	
	matched = 0
	alreadyAddedIDs = []
	eligibleListFound = []
	eligibleListNotFound = []
	with open('FCC_Active.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
			else:
				location_id, address_primary, city, state, zipCode, zip_suffix, unit_count, bsl_flag, building_type_code, land_use_code, address_confidence_code, county_geoid, block_geoid, H3_9, latitude, longitude = row
				address_primary = address_primary.upper().strip()
				city = city.upper().strip()
				state = state.upper().strip()
				if bsl_flag == 'True':
					if strippedAddress(address_primary) in addressesOnly:
						for item in eligibleList:
							eligible_Address, eligible_City, eligible_State, eligible_Zip, eligible_MbpsDown, eligible_MbpsUp= item
							eligible_City = eligible_City.upper()
							if (city.upper() == eligible_City.upper()) or (zipCode.strip() == eligible_Zip.strip()):
								if (strippedAddress(address_primary) == strippedAddress(eligible_Address)):
									if location_id not in alreadyAddedIDs:
										locationsToSave.append((location_id, address_primary, city, state, zipCode, zip_suffix, unit_count, bsl_flag, building_type_code, land_use_code, address_confidence_code, county_geoid, block_geoid, H3_9, latitude, longitude, eligible_MbpsDown, eligible_MbpsUp))
										alreadyAddedIDs.append(location_id)
										eligibleListFound.append(item)
										matched += 1
				line_count += 1
		print('Found ' + str(matched) + ' matching Broadband Fabric Data locations out of ' + str(len(eligibleAddressListWithSpeeds)) + ' total eligible locations. ')

	with open('bdcAvailability.csv', 'w') as csvfile:
		wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

		wr.writerow(('provider_id','brand_name','location_id','technology','max_advertised_download_speed','max_advertised_upload_speed','low_latency','business_residential_code'))
		for client in locationsToSave:
			location_id, address_primary, city, state, zipCode, zip_suffix, unit_count, bsl_flag, building_type_code, land_use_code, address_confidence_code, county_geoid, block_geoid, H3_9, latitude, longitude, MbpsDown, MbpsUp = client
			MbpsDown = int(MbpsDown)
			MbpsUp = int(MbpsUp)
			if (MbpsDown < 25) or (MbpsUp < 3):
				if (MbpsDown < 10) or (MbpsUp < 1):
					MbpsDown = 0
					MbpsUp = 0
				elif (MbpsDown >= 10) and (MbpsUp >= 1):
					MbpsDown = 10
					MbpsUp = 1
				else:
					raise NameError('Max bandwidth of upload or download were uninterpretable by FCC required rules.')
			wr.writerow((provider_id,brand_name,location_id,technology,MbpsDown,MbpsUp,low_latency,business_residential_code))

	for item in eligibleList:
		if item not in eligibleListFound:
			eligibleListNotFound.append(item)
			
	with open('notFound.csv', 'w') as csvfile:
		wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
		wr.writerow(('Address','City','State','Zip','Max Mbps Download','Max Mbps Upload'))
		for item in eligibleListNotFound:
			wr.writerow(item)
