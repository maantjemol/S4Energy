import parse_stations

def update():
  """
  Parameters:
    None

  Returns:
    None
  """
  # update de capiciteit CSV file
  data = parse_stations.parseStationsGPKG("./data/beschikbare_capaciteit_elektriciteitsnet.gpkg", 0, 0)
  parse_stations.writeStationsToCSV(data, "./output/beschikbare_capaciteit_elektriciteitsnet.csv")