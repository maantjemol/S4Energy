import geopandas as gpd
import geopy
import pandas as pd
import requests

def get_zip_code(point, geolocator):
    location = geolocator.reverse(f"{point.y}, {point.x}")
    return location.raw['address']['postcode']

def parseStationsGPKG(min_in: int, min_out: int):
  """
    Parses a GeoPackage file containing stations data and filters it
    based on several conditions.

    Args:
        filename: A string representing the path of the GeoPackage file.
        min_in: An integer representing the minimum value of beschikbare_capaciteit_invoeding_huidig_mva
                for a station to be included in the output.
        min_out: An integer representing the minimum value of beschikbare_capaciteit_afname_huidig_mva
                for a station to be included in the output.

    Returns:
        A GeoDataFrame containing the filtered data.
  """

  url = "https://service.pdok.nl/kadaster/netcapaciteit/atom/v1_0/downloads/beschikbare_capaciteit_elektriciteitsnet.gpkg"

  data = gpd.read_file(url)

  data["beschikbare_capaciteit_invoeding_huidig_mva"] = pd.to_numeric(data['beschikbare_capaciteit_invoeding_huidig_mva'],errors='coerce')
  data["beschikbare_capaciteit_afname_huidig_mva"] = pd.to_numeric(data['beschikbare_capaciteit_afname_huidig_mva'],errors='coerce')


  isExist = data["status"] != "Gepland, locatie onbekend" # Bestaat de locatie
  isGepland = data["status"] != "Gepland" # Bestaat de locatie
  isInvoeding = data["beschikbare_capaciteit_invoeding_huidig_mva"].notnull() # Is er invoeding mogelijk
  isAfname = data["beschikbare_capaciteit_afname_huidig_mva"].notnull() # Is er afname mogelijk
  isInvoedingGd0 = data["beschikbare_capaciteit_invoeding_huidig_mva"] > min_in # Is er invoeding groter dan 0
  isAfnameGd0 = data["beschikbare_capaciteit_afname_huidig_mva"] > min_out # Is er invoeding groter dan 0

  # Apply filters
  data = data[isExist]
  data = data[isGepland]
  data = data[isInvoeding]
  data = data[isAfname]

  data_all_stations = data.to_crs(epsg=4326)
  writeStationsToCSV(data_all_stations, "./output/all_stations.csv")

  data = data[isInvoedingGd0]
  data = data[isAfnameGd0]

  # Convert to geodataframe, use crs=4326
  data = data.to_crs(epsg=4326)

  # Get zipcode
  geolocator = geopy.Nominatim(user_agent="check_1")
  data["zip_code"] = data.apply(lambda x: get_zip_code(x.geometry.centroid, geolocator), axis=1)

  return data

def writeStationsToCSV(data, filename: str):
  csv_data = data.to_csv().replace("POINT ", "")
  #write data to file:
  with open(filename, "w") as f:
    f.write(csv_data)

if __name__ == "__main__":
  data = parseStationsGPKG(0, 0)
  writeStationsToCSV(data, "./output/beschikbare_capaciteit_elektriciteitsnet.csv")