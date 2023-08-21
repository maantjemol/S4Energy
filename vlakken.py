import requests
import geopandas as gpd
from shapely.geometry import Polygon
from math import radians, cos, sin, asin, sqrt


def get_vlakken(planID: str) -> list:
  headers = {
    'accept': 'application/hal+json',
    'Accept-Crs': 'epsg:4258',
    'X-Api-Key': 'l7ceb5f23326474774b0de37248b34ed0c',
  }

  params = {
    'page': '1',
    'pageSize': '10',
    'bestemmingshoofdgroep': 'bedrijf',
    'expand': 'geometrie',
  }

  response = requests.get(
    f'https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/{planID}/bestemmingsvlakken',
    params=params,
    headers=headers,
  )

  result = response.json()

  return result["_embedded"]["bestemmingsvlakken"]

def calc_area_and_centoid(coordinates) -> tuple:
  polygon = gpd.GeoSeries([Polygon(coordinates)], crs='EPSG:4258') # type: ignore
  centoid = polygon.centroid.item()
  polygon = polygon.to_crs({'proj':'cea'})
  area = polygon.area[0]
  return (area, centoid)


def calc_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of the Earth in kilometers
    return c * r * 1000

polygon = {
         "type":"Polygon",
         "coordinates":[
            [
               [
                  4.624698523,
                  51.914838731
               ],
               [
                  4.624312689,
                  51.914543045
               ],
               [
                  4.625321498,
                  51.913822748
               ],
               [
                  4.624185771,
                  51.912961027
               ],
               [
                  4.624411836,
                  51.912850702
               ],
               [
                  4.624481127,
                  51.912818613
               ],
               [
                  4.625549254,
                  51.912273007
               ],
               [
                  4.625647425,
                  51.912222857
               ],
               [
                  4.626396732,
                  51.911840658
               ],
               [
                  4.626951827,
                  51.911557107
               ],
               [
                  4.626807237,
                  51.911450241
               ],
               [
                  4.626623115,
                  51.911311614
               ],
               [
                  4.626374868,
                  51.911122568
               ],
               [
                  4.627157328,
                  51.910730989
               ],
               [
                  4.627037405,
                  51.910641173
               ],
               [
                  4.627870882,
                  51.910058363
               ],
               [
                  4.62788811,
                  51.910063985
               ],
               [
                  4.628117261,
                  51.910160106
               ],
               [
                  4.628152568,
                  51.910174392
               ],
               [
                  4.628182846,
                  51.910186183
               ],
               [
                  4.628223735,
                  51.910202105
               ],
               [
                  4.62826204,
                  51.910217031
               ],
               [
                  4.628394289,
                  51.910260338
               ],
               [
                  4.628503083,
                  51.910288024
               ],
               [
                  4.628609898,
                  51.910309037
               ],
               [
                  4.628675157,
                  51.91032082
               ],
               [
                  4.628769884,
                  51.910325242
               ],
               [
                  4.628843742,
                  51.910320991
               ],
               [
                  4.629002296,
                  51.910306688
               ],
               [
                  4.629195492,
                  51.910282299
               ],
               [
                  4.629456043,
                  51.910226505
               ],
               [
                  4.629556878,
                  51.910198796
               ],
               [
                  4.62967685,
                  51.910160029
               ],
               [
                  4.629809482,
                  51.910111725
               ],
               [
                  4.629901715,
                  51.910079538
               ],
               [
                  4.629962264,
                  51.910057789
               ],
               [
                  4.630002451,
                  51.910042965
               ],
               [
                  4.630027254,
                  51.910033812
               ],
               [
                  4.630051718,
                  51.910026626
               ],
               [
                  4.630086008,
                  51.910016834
               ],
               [
                  4.630154089,
                  51.909997399
               ],
               [
                  4.630273999,
                  51.909963169
               ],
               [
                  4.630520364,
                  51.909869243
               ],
               [
                  4.630579472,
                  51.909845902
               ],
               [
                  4.630606242,
                  51.909840717
               ],
               [
                  4.630678325,
                  51.909823573
               ],
               [
                  4.63073225,
                  51.909819695
               ],
               [
                  4.63078657,
                  51.909820018
               ],
               [
                  4.630859432,
                  51.909825628
               ],
               [
                  4.630882425,
                  51.909815214
               ],
               [
                  4.631116951,
                  51.909756284
               ],
               [
                  4.630006597,
                  51.910555028
               ],
               [
                  4.630251295,
                  51.910739801
               ],
               [
                  4.63044202,
                  51.910883813
               ],
               [
                  4.630685559,
                  51.911067706
               ],
               [
                  4.631372529,
                  51.911586427
               ],
               [
                  4.632217068,
                  51.912224089
               ],
               [
                  4.634532374,
                  51.913972128
               ],
               [
                  4.633626885,
                  51.914423471
               ],
               [
                  4.632367728,
                  51.915064372
               ],
               [
                  4.631235846,
                  51.915637135
               ],
               [
                  4.63027778,
                  51.916114829
               ],
               [
                  4.630132237,
                  51.916186475
               ],
               [
                  4.630049146,
                  51.916230928
               ],
               [
                  4.629953323,
                  51.916293321
               ],
               [
                  4.629537333,
                  51.916581333
               ],
               [
                  4.629485278,
                  51.916616862
               ],
               [
                  4.629248228,
                  51.916782586
               ],
               [
                  4.628878368,
                  51.91650397
               ],
               [
                  4.62847837,
                  51.916202669
               ],
               [
                  4.628065978,
                  51.915892011
               ],
               [
                  4.627666782,
                  51.915591288
               ],
               [
                  4.627271767,
                  51.915293718
               ],
               [
                  4.626868763,
                  51.914990118
               ],
               [
                  4.626478782,
                  51.914696336
               ],
               [
                  4.626254423,
                  51.914527308
               ],
               [
                  4.62546871,
                  51.915076199
               ],
               [
                  4.6254475,
                  51.915091018
               ],
               [
                  4.625234686,
                  51.915239695
               ],
               [
                  4.625216713,
                  51.915235849
               ],
               [
                  4.624698523,
                  51.914838731
               ]
            ]
         ]
      }

if __name__ == "__main__":
  print(calc_area_and_centoid(polygon['coordinates'][0]))
  print(calc_distance(4.629148367974661, 51.90479556716147, 4.6164225,51.8953804))