import requests, json, sys
from statistics import *
from datetime import datetime, date, timedelta

oneDay = timedelta(days=1)
oneMonth = timedelta(days=30)

hotspotsData = {'time': datetime.today()}


def getHotspotByName(name) :
    getHotspotInfo_URL = 'https://api.helium.io/v1/hotspots/name/{}'.format(name)
    res = requests.get(getHotspotInfo_URL)
    if res.status_code == 200 :
        return res.json()['data'][0]
    return None


def getWitnessesByHotspotAddress(address) :
    getWitnesses_URL = 'https://api.helium.io/v1/hotspots/{}/witnesses'.format(address)
    res = requests.get(getWitnesses_URL)
    if(res.status_code == 200) :
        return res.json()['data']
    return None


def getLastMonthRewards(address) :
    date_max = datetime.now() + oneDay
    date_min = datetime.now() - oneMonth
    getRewards_URL = 'https://api.helium.io/v1/hotspots/{}/rewards/sum?max_time={}&min_time={}'.format(address, date_max.isoformat(), date_min.isoformat())
    res = requests.get(getRewards_URL)
    if(res.status_code == 200) :
        return res.json()['data']['total']
    return None


def getLastDayRewards(address) :
    date_max = datetime.now() + oneDay
    date_min = datetime.now() - oneDay
    getRewards_URL = 'https://api.helium.io/v1/hotspots/{}/rewards/sum?max_time={}&min_time={}'.format(address, date_max.isoformat(), date_min.isoformat())
    res = requests.get(getRewards_URL)
    if(res.status_code == 200) :
        return res.json()['data']['total']
    return None


def displayResults() :
    print('Time : ' + str(hotspotsData['time']))
    print()
    for i in range(50) :
        if str(i) in hotspotsData :
            print('Number of Witnesses : {} | Number of hotspots : {} | Average HNT rewards (1 month) : {} | Average HNT rewards (1 day) : {} | Median HNT rewards (1 month) : {} | Median HNT rewards (1 day) : {}'  \
            .format(i, len(hotspotsData[str(i)]['totalLastMonthRewards']), \
            mean(hotspotsData[str(i)]['totalLastMonthRewards']), mean(hotspotsData[str(i)]['totalLastDayRewards']), \
            median(hotspotsData[str(i)]['totalLastMonthRewards']), median(hotspotsData[str(i)]['totalLastDayRewards'])))


def getResultsJson(filename) :
    try :
        with open(filename, 'r') as file :
            json_results = json.loads(file.read())
    except :
        with open(filename, 'w') as file :
            json_results = json.loads('{"data": []}')
    return json_results


def saveResultsJson(filename) : 
    results = getResultsJson(filename)
    str_data = '{{"time": "{}", '.format(str(datetime.today()))
    for i in range(50) :
        if str(i) in hotspotsData :
            str_data += '"{}": {{"nb_hotspot": {}, "avg_month": {}, "avg_day": {}, "median_month": {}, "median_day": {}}}'.format(i, len(hotspotsData[str(i)]['totalLastMonthRewards']), \
            mean(hotspotsData[str(i)]['totalLastMonthRewards']), mean(hotspotsData[str(i)]['totalLastDayRewards']), \
            median(hotspotsData[str(i)]['totalLastMonthRewards']), median(hotspotsData[str(i)]['totalLastDayRewards']))
            str_data += ','
    str_data = str_data[:len(str_data)-1]
    str_data += '}'
    print(str_data)
    results['data'].append(json.loads(str_data))
    with open(filename, 'w') as file :
        json.dump(results, file, indent=2)


if __name__ == '__main__' :
    if len(sys.argv) < 3 :
        print('ERROR: usage [output filename] [country id]')
        exit()
    output_path = sys.argv[1]
    country_id = sys.argv[2]

    hotspotsNames_URL = 'https://api.sitebot.com/api/v1/helium/hotspot-list.json?key=101687ce89a25521643d34b2ee3bb71e&country={}'.format(country_id)
    response = requests.get(hotspotsNames_URL)

    if response.status_code == 200 :
        hotspotsNames = response.json()['list']

        for hotspotName in hotspotsNames :
            name = hotspotName['name']
            print(name)
            hotspotInfo = getHotspotByName(name)
            if hotspotInfo is not None :
                address = hotspotInfo['address']
                if hotspotInfo['status']['online'] != 'online' :
                    address = None
                if address is not None:
                    witnesses = getWitnessesByHotspotAddress(address)
                    if witnesses is not None:
                        numberOfWitnesses = len(witnesses)
                    lastMonthRewards = getLastMonthRewards(address)
                    lastDayRewards = getLastDayRewards(address)
                    if lastMonthRewards is not None and lastDayRewards is not None:
                        if str(numberOfWitnesses) in hotspotsData :
                            hotspotsData[str(numberOfWitnesses)]['totalLastMonthRewards'].append(lastMonthRewards)
                            hotspotsData[str(numberOfWitnesses)]['totalLastDayRewards'].append(lastDayRewards)
                        else :
                            hotspotsData[str(numberOfWitnesses)] = {'totalLastMonthRewards': [lastMonthRewards], 'totalLastDayRewards': [lastDayRewards]}
                print('done')
        #displayResults()
        saveResultsJson(output_path)
