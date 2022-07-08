import csv
import requests
from geojson import Feature, FeatureCollection, Point, Polygon
from ipyleaflet import Map, GeoJSON
import folium
import json
from osgeo import gdal, ogr
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry import shape, mapping
import censusgeocode as cg
from ispSettings import provider_id, brand_name, low_latency, technology, business_residential_code

def pullEligibleAddresses():
	eligibleAddressList = []
	
	mostRecentUserID = None
	mostRecentCompanyName = ''
	with open('ucrm.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					header_store = row
					line_count += 1
				else:
					Id, CustomID, Firstname, Lastname, Name, Username, Companyname, IsLead, Clientlatitude, Clientlongitude, Companyregistrationnumber, CompanytaxID, Clienttaxrate1, Clienttaxrate2, Clienttaxrate3, Companywebsite, Emails, Phones, Address, Balance, Street1, Street2, City, Country, State, ZIPcode, InvoiceStreet1, InvoiceStreet2, InvoiceCity, InvoiceCountry, InvoiceState, InvoiceZIPcode, Invoiceaddresssameascontact, Registrationdate, Note, Archived, Service, Serviceperiod, Serviceindividualprice, Serviceinvoicelabel, Servicelatitude, Servicelongitude, Servicenote, Serviceactivefrom, Serviceactiveto, Serviceinvoicingfrom, Serviceinvoicingtype, Servicecontracttype, Servicecontractenddate, Serviceinvoicingperiodstartday, ServicecreateinvoiceXdaysinadvance, Serviceinvoiceseparately, Serviceinvoiceusecreditautomatically, Serviceminimumcontractlength, Servicesetupfee, Serviceearlyterminationfee, Serviceinvoiceapproveandsendautomatically, LocationID, Servicetax1, Servicetax2, Servicetax3, ServicecontractID, ServiceCensusBlockGEOID, Serviceprepaid = row
					if Id:
						mostRecentCompanyName = Companyname
					if not Id:
						Clientlatitude = Servicelatitude.replace("'","")
						Clientlongitude = Servicelongitude.replace("'","")
						
						if '|' in Service:
							planMbpsDown = int(Service.split(' | ')[1].split('/')[0])
							planMbpsUp = int(Service.split(' | ')[1].split('/')[1].split(' Mbps')[0])
						
						eligibleAddressList.append((Companyname, Street1, City, State, ZIPcode, Clientlatitude, Clientlongitude, planMbpsDown, planMbpsUp))
					line_count += 1

	srcDS = gdal.OpenEx('Service Area.kml')
	ds = gdal.VectorTranslate('coverage.geojson', srcDS, format='GeoJSON')
	del ds

	eligibleAddressListWithSpeeds = []

	geo_json_map = json.load(open('coverage.geojson'))

	for salesLead in eligibleAddressList:
		Companyname, Address, City, State, Zip, Latitude, Longitude, planMbpsDown, planMbpsUp = salesLead
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
				
		eligibleAddressListWithSpeeds.append((Companyname, Address, City, State, Zip, Latitude, Longitude, str(mbpsDownMax), str(mbpsUpMax)))
	
	return eligibleAddressListWithSpeeds

def geocodeCensusTract(lat, lon):
	result = cg.coordinates(x=lon, y=lat)
	tract = result['Census Tracts'][0]['GEOID']
	tract = str(tract)
	return tract

if __name__ == '__main__':
	locationsToSave = []
	eligibleList = []
	addressesOnly = []
	eligibleAddressListWithSpeeds = pullEligibleAddresses()
	
	knownCensusTract = []
	censusTractDownloadMbps = {}
	censusTractUploadMbps = {}
	censusTractConnections = {}
	censusTractConnectionsConsumer = {}
	
	for entry in eligibleAddressListWithSpeeds:
		Companyname, Address, City, State, Zip, Latitude, Longitude, MbpsDown, MbpsUp = entry
		try:
			censusTract = geocodeCensusTract(Latitude, Longitude)
			if censusTract not in knownCensusTract:
				censusTractDownloadMbps[censusTract] = MbpsDown
				censusTractUploadMbps[censusTract] = MbpsUp
				knownCensusTract.append(censusTract)
			else:
				if MbpsDown > censusTractDownloadMbps[censusTract]:
					censusTractDownloadMbps[censusTract] = MbpsDown
				if MbpsUp > censusTractUploadMbps[censusTract]:
					censusTractUploadMbps[censusTract] = MbpsUp
			
			if censusTract not in censusTractConnectionsConsumer:
				censusTractConnectionsConsumer[censusTract] = 0
			if censusTract not in censusTractConnections:
				censusTractConnections[censusTract] = 0
			
			if Companyname == '':
				censusTractConnectionsConsumer[censusTract] = censusTractConnectionsConsumer[censusTract] + 1
				censusTractConnections[censusTract] = censusTractConnections[censusTract] + 1
			else:
				censusTractConnections[censusTract] = censusTractConnections[censusTract] + 1
			
			print('Processing ' + Address)
		except:
			print('Failed to geocode ' + Address)
	
	with open('bdcSubscription.csv', 'w') as csvfile:
		wr = csv.writer(csvfile)
		#wr.writerow(('tract','technology','advertised_download_speed','advertised_upload_speed','total_connections','consumer_connections'))
		for censusTract in knownCensusTract:
			MbpsDown = censusTractDownloadMbps[censusTract]
			MbpsUp = censusTractUploadMbps[censusTract]
			totalConnections = censusTractConnections[censusTract]
			consumerConnections = censusTractConnectionsConsumer[censusTract]
			wr.writerow((censusTract,technology, MbpsDown,MbpsUp, totalConnections, consumerConnections))

			
