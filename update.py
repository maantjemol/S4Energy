import parse_stations

def update():
  """
  Parameters:
    None

  Returns:
    None
  """
  # update de capiciteit CSV file
  print("Getting stations")
  data = parse_stations.parseStationsGPKG(0, 0)
  parse_stations.writeStationsToCSV(data, "./output/beschikbare_capaciteit_elektriciteitsnet.csv")