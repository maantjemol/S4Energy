import sys
import argparse
import pandas as pd
sys.path.append('./modules')
import warnings
warnings.filterwarnings("ignore")

# import eigen modules
import parse_stations
import update
import plannen
import vlakken

# Add arguments
parser = argparse.ArgumentParser(description='Main script for updating the data')
parser.add_argument('--update', action='store_true', dest="update")
args = parser.parse_args()

# Update all the files if: > main.py --update
if args.update:
  update.update()

def generate_points(stations, range=1):
  new_stations = []
  for station in stations:
    cord = station["geometry"]
    lon_str, lat_str = cord.replace("(", "").replace(")", "").split(" ")
    lon, lat = float(lon_str), float(lat_str)
    station["points_around"] = [
      {
        "lon": lon,
        "lat": lat 
      },
      {
        "lon": lon + range * 0.01,
        "lat": lat 
      },
      {
        "lon": lon,
        "lat": lat + range * 0.006
      },
      {
        "lon": lon - range * 0.01,
        "lat": lat 
      },
      {
        "lon": lon,
        "lat": lat - range * 0.006
      },
    ]
    new_stations.append(station)
  return new_stations

def main():
  df_stations = pd.read_csv("./output/beschikbare_capaciteit_elektriciteitsnet.csv")
  
  stations = []
  for index, row in df_stations.iterrows():
    stations.append({
      "zip_code": row["zip_code"],
      "beschikbare_capaciteit_invoeding_huidig_mva": row["beschikbare_capaciteit_invoeding_huidig_mva"],
      "beschikbare_capaciteit_afname_huidig_mva": row["beschikbare_capaciteit_afname_huidig_mva"],
      "geometry": row["geometry"],
      "name": row["station"]
    })
  
  stations = generate_points(stations, range=1)

  new_stations = []
  i = 0
  for station in stations:
    i+= 1
    if i > float("inf"): 
      break
    print("> loading station", i, "van", len(stations))
    ruimtelijke_plannen = plannen.get_plan(station)
    station["plannen"] = ruimtelijke_plannen
    new_stations.append(station)
  
  # df = pd.DataFrame(columns=["zip_code", "beschikbare_capaciteit_invoeding_huidig_mva", "beschikbare_capaciteit_afname_huidig_mva", "station_location", "center_vlak", "area_vlak", "distance_to_vlak"]) # dataframe for the vlakken
  
  end_dictionary = {"zip_code": [], "beschikbare_capaciteit_invoeding_huidig_mva": [], "beschikbare_capaciteit_afname_huidig_mva": [], "station_lat": [], "station_long": [], "center_vlak_lat": [], "center_vlak_long": [], "area_vlak": [], "distance_to_station": [], "name": [] }

  stations = new_stations
  i = 0
  for station in stations:
    i+= 1
    print("> vlakken ophalen: ", i , "van", len(stations))
    bestemmings_vlakken = []
    j = 0
    for plan in station["plannen"]:
      j+= 1
      print("> vlakken ophalen: ", j, "van", len(station["plannen"]))
      # Get data for plan:
      vlak = vlakken.get_vlakken(plan["id"])
      bestemmings_vlakken.extend(vlak)
    
    print("> data berekenen...")
    for vlak in bestemmings_vlakken:
      try:
        # lon = x
        # lat = y
        area, center  = vlakken.calc_area_and_centoid(vlak["geometrie"]['coordinates'][0])
        lon_str, lat_str = station["geometry"].replace("(", "").replace(")", "").split(" ")
        lon, lat = float(lon_str), float(lat_str)
        distance = vlakken.calc_distance(lon, lat, center.x, center.y)
        
        # add data to dict
        end_dictionary["zip_code"].append(station["zip_code"])
        end_dictionary["name"].append(station["name"])
        end_dictionary["beschikbare_capaciteit_invoeding_huidig_mva"].append(station["beschikbare_capaciteit_invoeding_huidig_mva"])
        end_dictionary["beschikbare_capaciteit_afname_huidig_mva"].append(station["beschikbare_capaciteit_afname_huidig_mva"])
        end_dictionary["station_lat"].append(lat)
        end_dictionary["station_long"].append(lon)
        end_dictionary["center_vlak_lat"].append(center.y)
        end_dictionary["center_vlak_long"].append(center.x)
        end_dictionary["area_vlak"].append(area)
        end_dictionary["distance_to_station"].append(distance)
      except Exception as e:
        print("Couldn't parse it...", e)
    
  df = pd.DataFrame(end_dictionary)
  print(df.head())
  #save dataframe to csv
  df.to_csv("./output/station_data.csv")
    


def test():
  print("> RUNNING TEST!")
  print("> Loading data...")
  df_stations = pd.read_csv("./output/beschikbare_capaciteit_elektriciteitsnet.csv")
  
  stations = []
  for index, row in df_stations.iterrows():
    stations.append({
      "zip_code": row["zip_code"],
      "beschikbare_capaciteit_invoeding_huidig_mva": row["beschikbare_capaciteit_invoeding_huidig_mva"],
      "beschikbare_capaciteit_afname_huidig_mva": row["beschikbare_capaciteit_afname_huidig_mva"],
      "geometry": row["geometry"]
    })
  
  print("> Generating points...")
  stations = generate_points(stations)

  print("> Requesting plannen...")
  station = stations[0]
  ruimtelijke_plannen = plannen.get_plan(station)
  station["plannen"] = ruimtelijke_plannen
  print(station)
  bestemmings_vlakken = []
  print("> Requesting vlakken...")


  for plan in station["plannen"]:
    # print(plan)
    # Get data for plan:
    vlak = vlakken.get_vlakken(plan["id"])
    bestemmings_vlakken.extend(vlak)
  for vlak in bestemmings_vlakken:
    try:
      area, center  = vlakken.calc_area_and_centoid(vlak["geometrie"]['coordinates'][0])
      print(center)
    except:
      print("Couldn't parse it...")
  
  # pandas dataframe:
  # "zip_code", "beschikbare_capaciteit_invoeding_huidig_mva", "beschikbare_capaciteit_afname_huidig_mva", "station_location", "center_vlak", "area_vlak", "distance_to_vlak"


if __name__ == "__main__":
  main()
  # test()

