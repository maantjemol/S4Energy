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

def getCoordsFromZip(zip: str):
  # geolocator = geopy.Nominatim(user_agent="check_1")
  # location = geolocator.geocode({"postalcode": zip, "country": "Netherlands"})
  response = requests.get(f"https://nominatim.openstreetmap.org/search?postalcode={zip}&country=Netherlands&format=json&limit=1")
  if len(response.json()) == 0:
    return (0, 0)
  location = response.json()[0]
  return f'{(float(location["lat"]), float(location["lon"]))}'.replace(",", "")

def getCoordsFromAdress(adress: str):
  # geolocator = geopy.Nominatim(user_agent="check_1")
  # location = geolocator.geocode({"postalcode": zip, "country": "Netherlands"})
  response = requests.get(f"https://nominatim.openstreetmap.org/search?street={adress}&country=netherlands&format=json&limit=1")
  if len(response.json()) == 0:
    return "(0 0)"
  location = response.json()[0]
  return f'{(float(location["lat"]), float(location["lon"]))}'.replace(",", "")

adress_cord = [["(52.368039555 4.918637895000001)",	"Hoogte Kadijk 400"],
["(52.3997431 4.90456305)",	"Klaprozenweg 58"],
["(52.3997431 4.90456305)",""],
["(0 0)",	"Nwe Hemweg 25"],
["(52.3426971 4.8110566)",	"Andelechtlaan nb 250"],
["(52.33753207356828 4.877493570484582)",	"Drentestraat 8"],
["(52.354947790909094 4.9289447)",""],
["(0 0)",	"Borchlandweg parkeerterrein Arena P2"],
["(52.29532195 4.94814415)",	"Schurenbergweg 10 nb Meibergdreef"],
["(52.341565460000005 5.0101102200000005)",	"Over Diemerweg 35"],
["(52.341565460000005 5.0101102200000005)",	"Overdiemerweg 35"],
["(52.3334417 4.967589555555556)",	"Visseringweg 10"],
["(52.29276147687861 4.880595901156069)",	"Langs de Akker na volkstuinen"],
["(52.25958755 5.1233474333333335)",	"Stichtsekade 44"],
["(52.368980930769226 5.174599446153846)",	"Jaques Brellweg 53"],
["(52.38662089756098 5.215405156097561)",	"Markerkant 12-10"],
["(52.3593520625 5.262025175)",	"Strubbenweg 37"],
["(52.402626 5.2629300084745765)",	"Zandzuigerstraat 1"],
["(52.503918590909095 4.901351854545455)",	"Noorderweg nb 134"],
["(52.428206 4.8762872)",	"Verlengde Stellingweg 1"],
["(52.69855263181818 5.11958825)",	"Zwaagdijk 229"],
["(52.87890516296296 4.784336966666666)",	"Molenvaart nabij 545"],
["(52.635684033333334 4.8547520833333335)",	"Huigendijk 43"],
["(52.47396427142857 4.677862419047619)",	"Gooilaan 39b"],
["(52.4716457 4.63257805)",	"Hoflaan 1"],
["(52.396505593877556 4.663595924489796)",	"Emrikweg 1"],
["(52.31107518 4.64390356)",	"Leenderbos 95"],
["(52.37331290757576 4.702600122727272)",	"Spaarnwouderweg t.o. 1175"],
["(52.37331290757576 4.702600122727272)",""],
["(52.23376185 4.52440075)",	"Carolus Clusiuslaan 32"],
["(52.07541929655172 4.3395333)",	"Von Geusaustraat 193"],
["(52.0413965 4.293836322222222)",	"Sammersweg 4a"],
["(52.16582842222222 4.495700433333334)",	"Koningstraat 41"],
["(52.128255965178575 4.637909852678572)",	"A.v.Leeuwenhoekweg 46"],
["(52.03617964871795 4.355872397435897)",""],
["(52.076749668 4.2916345840000005)",	"Constant Rebequeplein 20"],
["(52.03455481489362 4.276294985106383)",""],
["(52.03455481489362 4.276294985106383)",""],
["(51.98966698 4.3694494)",	"Energieweg 15"],
["(0 0)",""],
["(0 0)",	"Zoetermeerselaan 18"],
["(51.980714 4.220597933333334)","Burgemeester Elsenweg ( na nr. 45)"],
["(51.97796623125 4.257765102083334)",	"Burgemeester Elsenweg 41"],
["(51.98054865 4.245879085714286)",	"Kade van As 4-6"],
["(52.04484747 4.5181672100000005)",	"Werner van Siemensstraat 61"],
["(52.03946446666667 4.647094955555556)",	"Limaweg 51"],
["(52.00711798333333 4.7347556)",	"Provincialeweg west 70"],
["(51.91242496666667 4.629477766666667)",	"Edisonstraat 1"],
["(51.91242496666667 4.629477766666667)",	"Edisonstraat 1"],
["(51.85142705263158 4.66916752631579)",	"Staalindustrieweg 32"],
["(0 0)",	"St. Jobsstraat 60"],
["(51.90990859090909 4.424191318181818)",	"Galieleistraat 7"],
["(51.9582437105 4.5407364985)",	"Vlambloem 71"],
["(51.876949180000004 4.5028659)",	"Slinge 11"],
["(51.8879579 4.4150465)",	"Eemlandweg 19"],
["(0 0)",	"Peterolieumweg 46"],
["(51.88126730909091 4.331796109090909)",	"Vondelingenweg 601"],
["(51.87571623636364 4.288410868181818)","Botlekweg 131 (Havennr. 4090)"],
["(51.8955066375 4.2821393375)",	"Prof. Gerbrandyweg 10 (Havennr. 4506)"],
["(51.88545389166667 4.244604170833334)",	"Theemsweg 24"],
["(51.919999477551016 4.1833213795918365)",	"Moeselweg 401 (Havennr. 5802)"],
["(51.95552384 4.0251488)",	"Coloradoweg 10"],
["(51.95552384 4.0251488)",	"Coloradoweg 10"],
["(51.95552384 4.0251488)",	"Coloradoweg 4"],
["(0 0)",	"Oudelandseweg 259"],
["(51.8632114625 4.2665515625)",	"Noorddijk 4"],
["(0 0)",	"Oud Hoenderhoekseweg 10"],
["(0 0)",	"Merseyweg 10"],
["(51.81537225384616 4.679901438461538)",	"Noordendijk 258"],
["(51.81538049545454 4.7271387727272725)",	"Baanhoekweg 15"],
["(51.81538049545454 4.7271387727272725)",	"Baanhoekweg 2c"],
["(51.79047955714286 4.683094196428572)",	"Oudendijk 13"],
["(52.05221703684211 5.122898621052632)",	"Laagraven"],
["(52.07886611111111 5.041706594444444)",	"Heijcopperkade .. (achter huisnr. 2)"],
["(52.10712423214286 5.067638557142858)",	"Atoomweg 7-9"],
["(0 0)",	"Kortrijk"],
["(52.176660738461536 4.996379807692308)",	"Ter Aarseweg .. (naast huisnr. 1)"],
["(52.238635255 5.392351435)",	"Groenweg .. (naast huisnr. 6)"],
["(52.16941197241379 5.330397631034483)",	"Peter v.d. Bremerweg .. (naast huisnr. 21)"],
["(52.161961640625 5.613700221875)",	"Wencopperweg 46"],
["(52.32309923636364 5.653709909090909)",	"Leuvenumseweg 34"],
["(52.3483160952381 5.459953071428572)",	"Bloesemlaan 21"],
["(52.01108164153846 5.571339647692308)",	"Wageningselaan 60"],
["(0 0)",	"t Goeie Spoor"],
["(52.05768757777778 5.2668768111111115)",	"Kleine Loolaan 12"],
["(51.89756988333333 5.444434333333334)",	"Schootslaan Wethouder 4"],
["(51.86712193333333 4.987686)",	"Parallelweg"],
["(51.7837499 4.7714943)",	"Boomgatweg 2"],
["(51.48954327916667 3.6465716458333337)",	"Elektraweg"],
["(51.443961814285714 3.56847065)",""],
["(51.45604599333333 3.7039732666666665)",	"Frankrijkweg 2"],
["(51.41633505 4.17886950625)","Westelijke Spuikanaalweg .. (ter hoogte van de A58)"],
["(51.44145064285714 4.2365039)",	"Bathpolderdwarsweg .."],
["(51.45543998611111 4.024839825)",	"Zanddijk"],
["(0 0)","Eversdijkseweg .. (ter hoogte van de A58)"],
["(51.423723130769226 3.7351187307692304)",	"Wilhelminahofweg"],
["(51.423723130769226 3.7351187307692304)",	"Wilhelminahofweg 1"],
["(0 0)",	"Poelweg"],
["(51.32550128857143 3.4885141685714283)",	"Lange Heerenstraat .. (ter hoogte van de N58)"],
["(51.33362044285714 3.8320070785714284)",	"Herbert H. Dowweg"],
["(51.33401757666667 3.828096743333333)",	"Industrieweg"],
["(51.33401757666667 3.828096743333333)",	"Westkade"],
["(51.49100374 4.2938275)",	"Obrechtlaan Jacob 5-7"],
["(51.50079055384616 4.270807026923077)",	"Lelyweg 17"],
["(51.467626896 4.3074895920000005)",	"Antwerpsestraatweg 560"],
["(51.54551590526316 4.483353705263158)",""],
["(51.54551590526316 4.483353705263158)",	"Zwaanhoefstraat 16"],
["(0 0)",	"Nieuwendijk 22a"],
["(51.66151205 4.58580645)",	"Keenenweg 22a"],
["(51.68255572857143 4.6666954857142855)",	"Oude Moerdijkseweg 1"],
["(51.58212332 4.72979632)",	"Kruisvoort 89"],
["(51.61673810714286 4.771447207142858)",	"Terheijdenseweg 259"],
["(51.57268878461539 4.608683215384615)",	"Vossendaal 31"],
["(51.64589354285714 4.926482328571429)",	"Hogedijk 38"],
["(51.69337058333333 4.842364575)",	"Centraleweg 7b"],
["(51.699279625 4.83530975)",	"Peuzelaar 1"],
["(51.5983695375 5.0859633625)",	"Kalverstraat 48"],
["(0 0)",	"Katsbogte 35"],
["(51.59780194 5.0250234)",	"Zeusstraat 1"],
["(51.70940575 5.090251164285714)",	"Valkenvoortweg 11"],
["(51.70987599473685 5.269499239473684)",	"Graaf van Solmsweg 26"],
["(51.708512516666666 5.298800744444445)",	"Orthen 63"],
["(51.55931382 5.38493605)",	"Horsterweg 132"],
["(51.79867352 5.2750727799999995)",	"Bommelsekade"],
["(51.76363588541667 5.548782604166666)",	"Landweerstraat 132"],
["(0 0)",	"Belgenlaan 9"],
["(0 0)",	"Raamweg 1"],
["(51.6800487 5.882579466666666)",	"Rijkevoortseweg 1b"],
["(51.6068977625 5.489816425)",	"Dalenstraat 7"],
["(51.3738976875 5.2690974875)",	"Zwartven 7"],
["(51.45911565 5.4469305)",	"Vredeoord 10"],
["(51.44671284026549 5.523688378318584)",	"Daalakkerweg 26"],
["(51.44671284026549 5.523688378318584)",	"Daalakkersweg 26"],
["(51.41679878888889 5.4686762)",	"Genneperweg 201"],
["(51.425232745833334 5.4314942041666665)",	"Langendijk 3"],
["(51.488923 5.418231125)",	"Ploegstraat 4"],
["(0 0)",	"Hogeweg 13"],
["(51.459458989999995 5.692316796666667)",	"Varenschut 4"],
["(51.46059306666667 5.664803766666666)",	"Lungendonk 21"],
["(51.511472012903226 5.669687374193549)",	"Bakelseweg 10"],
["(51.539606440178574 5.990768574107142)",	"Keizersveld 26"],
["(51.64495438666667 5.9341732)",	"Zandkant 3"],
["(51.64495438666667 5.9341732)",	"Zandkant 1"],
["(51.39076636666667 6.103470422222222)",	"James Cookweg 3"],
["(51.32229306666667 6.1187170962962965)",	"Rijksweg Noord 52"],
["(51.310828955 5.985270625)",	"Keup 17"],
["(51.25208446827957 5.644994318817204)",	"Trencheeweg 12"],
["(51.263234477272725 5.7184637227272725)",	"Helmondseweg 30"],
["(51.26179477916667 5.725849948611112)",	"Graafschap Hornelaan 180"],
["(0 0)",	"Hoofdstraat 1"],
["(51.32333406666667 5.640850853333333)",	"Panweg 2"],
["(51.23741583076923 5.817801630769231)",	"Kelperweg 28a"],
["(51.181987831578944 5.9781053421052635)",	"Roerderweg 56"],
["(0 0)",	"Schepersweg 1a"],
["(0 0)",	"Linnerweg 12"],
["(51.148369496 5.912659468)",	"Broekstraat 30"],
["(51.22969661818182 6.010924990909091)",	"Maalbroekkerveldweg 1"],
["(51.22710602 5.966200339999999)",	"Roermondseweg 57"],
["(0 0)",	"Holtummerweg 1"],
["(50.981355508571426 5.816750808571429)",	"Valderenstraat 23"],
["(0 0)",	"Urmonderbaan"],
["(51.00023155 5.796029)",	"Bergerweg 120"],
["(50.9436878 5.808026133333334)",	"Huynhof 20"],
["(50.86404883684211 5.707017447368421)",	"Sionsweg 39a"],
["(50.859251475 5.88679865)",	"Ransdalerstraat 1"],
["(50.89704619411765 5.9688690705882355)",	"Huskensweg 35"],
["(50.90097273846153 5.965257976923077)",	"Huskensweg 84a"],
["(0 0)",	"Rukkersweg 130a"],
["(50.93535635 5.9435470625)",	"Planeetstraat 7a"],
["(51.824545428571426 5.820476804761904)",	"Gerstweg 2"],
["(51.8208884325 5.7820655924999995)",	"Rozenburgweg 150"],
["(51.85362896081081 5.843095823648649)",	"Winselingseweg 40"],
["(51.706012930769226 5.976572215384615)",	"Moutstraat 23"],
["(51.8770983 5.5784102)",	"Noordzuid"],
["(0 0)",	"Laar De 24"],
["(51.92335696 5.65490064)",	"De Zandvoort1"],
["(51.93051011428572 5.678869007142858)",	"Gesperendensestraat 8"],
["(52.03446731948052 5.6291344)",	"Frankeneng 116"],
["(52.02810102 5.6374401700000005)",	"Dieselstraat"],
["(52.05294556666667 5.666622966666666)",	"Knuttelweg 9"],
["(51.98417277741935 5.875017269354839)",	"Utrechtseweg 310"],
["(51.98417277741935 5.875017269354839)",	"Utrechtseweg 310"],
["(51.98417277741935 5.875017269354839)",	"Utrechtseweg 310"],
["(52.03154115 5.887599325)",	"Deelenseweg 1"],
["(51.975565585000005 5.91915267)",	"Broekstraat 20a"],
["(51.9665212 5.7228864)",	"Bokkedijk"],
["(51.9402481 6.078764252941176)",	"Einsteinstraat 85"],
["(52.096453128571426 6.0641203)",	"Schoonmansmolenweg 5"],
["(51.98170315 6.2529601)",	"Rouwenoordseweg 12"],
["(51.98170315 6.2529601)",	"Rouwenoordseweg 10"],
["(51.97259022 6.27498734)",	"Keppelseweg 131"],
["(51.90528408888889 6.374802111111111)",	"Over de Ijssel 7"],
["(51.975929825 6.68718331875)",	"Mentinkweg 2a"],
["(51.945088278571426 6.5765560857142855)",	"Barloseweg 6-1"],
["(52.11563954 6.64214678)",	"Needseweg 18"],
["(52.149942278260866 6.221441626086956)",	"Voorsterallee 74d"],
["(52.16579587 6.371941120000001)",	"Kanaaldijk"],
["(52.12187243333333 6.53607645)",	"Hesselink Es 16"],
["(52.19769486923077 6.036579692307692)",	"IJsseldijk 41"],
["(52.20149491363636 5.970043645454545)",	"Beekbergerweg Oude 25"],
["(52.2762991 6.1348795)",	"Wetermansweg 4a"],
["(52.24133234 6.19140232)",	"Londenstraat 1a"],
["(52.372041575 6.46904325)",	"Helmkruidlaan 4"],
["(52.3022939 6.4753372)",	"Bovenleiding 1"],
["(52.2464847 6.5935106)",	"Enterseweg 10"],
["(52.1498744 6.715035333333333)",	"Demmertweg 4"],
["(52.227551094999995 6.8667045)",	"G.J. van Heekstraat"],
["(52.2358712 6.9030384950000006)",	"Vechtstraat 40"],
["(52.198107236666665 6.88505387)",	"Vlierstraat 115"],
["(52.21458195 6.8325341)",	"Geerdinkzijdeweg 39"],
["(0 0)",	"Boldershoekweg 51"],
["(52.246438705882355 6.753521364705883)",	"Vockersweg 5"],
["(52.246438705882355 6.753521364705883)",	"Vockersweg 3"],
["(52.24518857777778 6.795075644444445)",	"Boortorenweg 27"],
["(52.24176361111111 6.773158433333333)",	"Diamantstraat 35"],
["(52.27276259285714 6.779127614285715)",	"Slachthuisweg 201"],
["(52.304482771428574 6.918586342857143)",	"Grondmanstraat 28"],
["(52.25064422321429 7.007314742857143)",	"De Zoeker Esch 10"],
["(52.338295425 6.68875835)",	"Planthofsweg 77"],
["(52.356029430769226 6.646071723076923)",	"Wierdensestraat 157h"],
["(52.316606058333335 6.6700928416666665)",	"Maatkampsweg 7a"],
["(52.3933128125 6.76623248125)",	"Kluunvenweg 9"],
["(52.44879217222222 6.566448855555556)",	"De Sluis 25"],
["(52.60587404166667 6.4869348166666665)",	"Rollepaal 7"],
["(52.52822503636364 6.410145113636363)",	"Kievitstraat 1"],
["(52.50569249130435 6.355307456521739)",	"Vilsterse Allee 11a"],
["(52.66837079166667 6.69973595)",	"Dreef 2"],
["(52.64757706666667 6.7439794666666675)",	"Vosmatenweg 7"],
["(52.65761478333333 6.897210933333333)",""],
["(52.57544656666667 6.5984571333333335)",	"Stelling 6"],
["(52.772298215789476 6.908273692105263)",	"Eerste Bokslootweg 17"],
["(52.801959625 6.903700225)",	"Woldweg/N391"],
["(52.801959625 6.903700225)",	"Weerdingerstraat (achter huisnr. 180)"],
["(52.75883005675676 6.929505935135135)",	"Phileas Foggstraat 26"],
["(0 0)",	"Sint Gerardusstraat"],
["(52.71602286666667 6.843379933333333)",	"Nieuweweg tussen 14 en 44"],
["(52.695321248571425 6.90590272)",	"Beekweg 12"],
["(0 0)",	"Zwet 20"],
["(52.73993663157895 6.474024652631579)",	"Toldijk 31"],
["(52.73703891428571 6.4685076285714285)",	"Stroom 2"],
["(52.683081236363634 6.184646645454546)",	"Westerstouwe 8"],
["(52.497294010000005 6.122990305)",	"Marsweg 5"],
["(52.477794576190476 6.114691161904762)",	"IJsselcentraleweg 6"],
["(52.531373333333335 6.189336516666667)",	"Berkummerbroekweg 24"],
["(52.531373333333335 6.189336516666667)",	"Berkummerbroekweg 26"],
["(52.531373333333335 6.189336516666667)",	"Berkummerbroekweg 24"],
["(52.52176371428571 6.0677912)",	"Frankhuisweg 24a"],
["(52.45348005555556 6.079716744444445)",	"Kanaaldijk 1a"],
["(52.626705775 6.088191475)",	"De Velde 1"],
["(52.37561255 6.2694168)",	"Westdorplaan 211"],
["(52.355582428571424 6.1245252571428574)",	"Holsterweg 46a"],
["(52.30869896666667 5.988308558333333)",	"Achterdorperweg 15"],
["(0 0)",	"Dronterweg 14"],
["(52.5577688 5.4785474)",	"Ijsselmeerdijk 33"],
["(52.5752432 5.5344761)",	"Ijsselmeerdijk 111"],
["(52.50606949791667 5.47465914375)",	"Zilverparkkade 18-19"],
["(52.51790501428572 5.658557914285714)",	"Dronterweg 19"],
["(52.47936804285714 5.6556476714285715)",	"Rietweg 55"],
["(52.56734196666667 5.86111344)",	"Eastmanstraat 4"],
["(52.69547426923077 5.757831603846154)",	"Nagelerweg 16a"],
["(52.61387528235294 5.8016962)",	"Ramsweg 8a"],
["(52.61387528235294 5.8016962)",	"Ramsweg 8a"],
["(52.77663182941176 5.851519623529412)",	"Uiterdijkenweg tussen 15 en 17"],
["(52.67902364285714 5.924676385714286)",	"Voorsterweg 31"],
["(52.678888836842106 5.942743942105263)",	"De Voorst 61"],
["(52.7792888 6.1434952)",	"Bedelaarspad 2"],
["(52.99444419411765 6.077967982352941)",	"Neijewei 93-94"],
["(52.9919698877193 6.272954814035088)",	"Nanningaweg 47a"],
["(52.97005581578947 5.912363668421053)",	"Schans 30"],
["(52.9674999 5.906046)",	"Haulerweg 12"],
["(52.97309465 5.8677166)",	"De Dolten 7"],
["(52.97309465 5.8677166)",	"De Dolten 7"],
["(52.84923497 5.72579597)",	"Pasveer 3"],
["(53.03743831111111 5.676896066666666)",	"Groenedijk 3"],
["(0 0)",	"Marneweg 1"],
["(53.18121084285714 5.5035392)",	"Kiesterzijl 50"],
["(53.19649577692308 5.772741692307692)",	"Voltastraat 7a1"],
["(53.20221075 5.824491466666666)",	"Kanaalweg 191"],
["(53.10021288461539 5.741833107692308)",	"Snitserdyk 9"],
["(53.10611310769231 6.069167076923077)",	"Tussendiepen 37"],
["(0 0)",	"Koumarwei 2"],
["(0 0)",	"Koumarwei 2"],
["(0 0)",	"Betterwird 32"],
["(0 0)",	"Rustenburgerweg 1B"],
["(0 0)",	"Rustenburgerweg 1B"],
["(53.1873735125 5.8639883625)",	"Rustenburgerweg 1a"],
["(53.090051 6.4305494)",	"Westerstukkenweg 2"],
["(53.01272495 6.592364025)",	"Marsdijk 13"],
["(53.003858215 6.525538785)",	"Asserwijk 52"],
["(53.003858215 6.525538785)",	"Asserwijk 52"],
["(52.8604997 6.511400055555555)",	"De Lotten 1"],
["(52.794677475 6.51602315)",	"Vamweg 7"],
["(52.794677475 6.51602315)",	"Oosterveldseweg"],
["(52.97416475 6.96790085)",	"Electronicaweg 14"],
["(52.982093866666666 6.83484321111111)",	"Noorderdwarsdijk 1"],
["(0 0)",	"Handelsweg"],
["(52.9219214 7.05063735)",	"M en O Weg 11"],
["(0 0)",	"Schaapsbergweg 58"],
["(53.1552565 6.722457576923077)",	"Woldweg 68"],
["(53.1552565 6.722457576923077)",	"Woldweg 68"],
["(53.201789536363634 6.766753454545455)",	"Groeneweg"],
["(0 0)",	"Leemens"],
["(53.26627659230769 6.769407246153847)",	"Meenteweg 6"],
["(53.2683103 6.7335933)",	"Dellerweerden"],
["(53.293712 6.82500645)",	"Schildweg 2"],
["(53.25938246666667 6.882405183333333)",	"Oosterzandenweg 7"],
["(53.25938246666667 6.882405183333333)",""],
["(53.25938246666667 6.882405183333333)",""],
["(53.175441985714286 6.8316236)",	"Spitsbergen 3"],
["(53.09623935833333 6.884385725)",	"Noorderweg"],
["(53.09623935833333 6.884385725)",	"Adriaan Tripweg 7"],
["(53.135935446666664 6.866282259999999)",	"Daaleweg"],
["(53.12859007857143 6.932059564285715)",	"Beneden Veensloot 55"],
["(53.12787957142857 6.943799028571428)",	"Wethouder L. Veenmanweg 11"],
["(53.12859007857143 6.932059564285715)",	"Beneden Veensloot 71"],
["(53.13543225 7.046616016666667)",	"J.A. Koningstraat 50"],
["(0 0)",	"Kanaalweg"],
["(53.16247914285714 6.993737742857143)",	"Oudedijksterweg"],
["(0 0)",	"Bloemsingel 19"],
["(53.214663063636365 6.579904238636363)",	"Winschoterdiep 50"],
["(53.21107094166667 6.595096166666666)",	"Bornholmstraat 23"],
["(0 0)",	"Van Heemskerckstraat 77"],
["(53.24637435714286 6.587884807142857)",	"Ideweersterweg 4W1"],
["(53.21051409 6.47428226)",	"Hoendiep 330"],
["(53.21051409 6.47428226)",	"Hoendiep 330"],
["(53.281426321428576 6.3049792857142855)",	"Waardweg 5"],
["(53.3043489 6.463907666666667)",	"Meendenerweg"],
["(53.31274794444444 6.966146622222222)",	"Oosterhorn 2"],
["(53.31274794444444 6.966146622222222)",	"Oosterhorn 20"],
["(53.31274794444444 6.966146622222222)",	"Oosterhorn 4"],
["(0 0)",	"Oosterlaan 2"],
["(53.2848444 6.9385337)",	"Westerlaan/N991"],
["(0 0)",	"Scheemderzwaag"],
["(53.35795448333333 6.5001383)",	"Maarhuizerweg 6"],
["(53.433603285714284 6.864575092857144)",	"Robbenplaatweg 9"],
["(53.433603285714284 6.864575092857144)",	"Robbenplaatweg 31"],
["(0 0)",	"Robbenplaatweg 31"],
["(0 0)",	"Robbenplaatweg 21"],
["(0 0)",	"Robbenplaatweg 31"],
["(0 0)",	"Hubertgatweg 1"],
["(0 0)",	"Scheldelaan 600"]]

def get_zip(lat, lon):
  url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
  response = requests.get(url)
  data = response.json()
  if "address" not in data:
    print("No address found")
    return None
  print(data["address"]["postcode"])
  return data["address"]["postcode"]

def wtfhapp ():
  data = pd.read_csv("./output/all_stations_more.csv")
  # geometry =  (5.671088774486666 51.51036164155714)
  data["latitude"] = data["geometry"].apply(lambda x: float(x.split(" ")[1].replace(")", "")))
  data["longitude"] = data["geometry"].apply(lambda x: float(x.split(" ")[0].replace("(", "")))
  data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))
  # Convert to geodataframe, use crs=4326

  # Get zipcode
  data["zip_code"] = data.apply(lambda x: get_zip(x.geometry.centroid.x, x.geometry.centroid.y), axis=1)

  # remove lat and lon columns from dataframe:
  data = data.drop(columns=["longitude", "latitude"])

  return data

if __name__ == "__main__":
  data = wtfhapp()
  writeStationsToCSV(data, "./output/beschikbare_capaciteit_elektriciteitsnet_2.csv")
