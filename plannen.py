import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

def plan_request(lat: float, lon: float):
  headers = {
    'accept': 'application/hal+json',
    'Content-Crs': 'epsg:4258',
    'Accept-Crs': 'epsg:4258',
    'X-Api-Key': os.getenv('API_KEY'),
    'Content-Type': 'application/json',
  }

  params = {
    'page': '1',
    'pageSize': '10',
    'beleidsmatigVerantwoordelijkeOverheid.type': 'gemeentelijke overheid',
    'publicerendBevoegdGezag.type': 'gemeentelijke overheid',
    'planType': 'bestemmingsplan',
    'regelStatus': 'geldend',
  }

  json_data = {
    '_geo': {
    'contains': {
      'type': 'Point',
      'coordinates': [
        lon,
        lat,
      ]},
    },
  }

  response = requests.post(
      'https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/_zoek',
      params=params,
      headers=headers,
      json=json_data,
  )

  return response.json()

def filter_unique_plans(plannen):
  unique_plans = []
  for plan in plannen:
    if plan not in unique_plans:
      unique_plans.append(plan)
  return unique_plans

def get_plan(station):
  coords = station["points_around"]
  plannen = []
  for coord in coords:
    lon = coord["lon"]
    lat = coord["lat"]
    res = plan_request(lat, lon)
    for plan in res["_embedded"]["plannen"]:
      plan = {
        "id": plan["id"],
        "naam": plan["naam"],
        "parapluplan": plan["isParapluplan"],
      }
      if not plan['parapluplan']:
        plannen.append(plan)
  return filter_unique_plans(plannen)

 