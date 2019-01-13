from steam import SteamClient
from csgo import CSGOClient
from csgo.enums import ECsgoGCMsg
import gevent
import requests
from requests import exceptions
import json

from gevent import sleep
import struct
import sqlite3
import externalLists

def Get_Inspects(current_market_link, alreadyHave, db, c, fail):
    temp_price = []
    temp_inspect = []
    urlextender = '/render/?query=&start=0&count=100&currency=1'
    n = 0
    try:
        request = requests.get(current_market_link + urlextender)
        data = request.text.split('"listinginfo":')[1].split(',"assets":')[0]
        data = json.loads(data)
        for marketID in data:
            price = int(data[marketID]['converted_price']) + int(data[marketID]['converted_fee'])
            padded = "%03d" % (price,)
            price = padded[0:-2] + '.' + padded[-2:]
            price = float(price)
            link = data[marketID]['asset']['market_actions'][0]['link']
            assetID = data[marketID]['asset']['id']
            inspectlink = link.replace('%assetid%', assetID).replace('%listingid%', marketID)
            if (inspectlink not in alreadyHave):
                if ('StatTrak' in current_market_link):
                    temp_inspect.append('yes')
                if ('StatTrak' not in current_market_link):
                    temp_inspect.append('no')
                temp_inspect.append(inspectlink)
                temp_price.append(price)
                c.execute("INSERT INTO inspectsTable(inspects) VALUES (?)", (inspectlink,))
                db.commit()
                n += 1
        print("Aquired %s new inspect links from %s. Waiting 10 seconds..." % (n, current_market_link))
        gevent.sleep(10)

        if (len(temp_inspect) > 0):
            inspect_price_temp = [temp_inspect, temp_price]
            return inspect_price_temp
        else:
            inspect_price_temp = ['none']
            return inspect_price_temp
    except:
        if (fail == 0):
            fail = 1
            inspect_price_temp = ['fail']
            return inspect_price_temp
        
def CSGO_Check_Item(param_a, param_d, param_m, cs):
    try:
        cs.send(ECsgoGCMsg.EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockRequest,
            {
                'param_s': 0,
                'param_a': param_a,
                'param_d': param_d,
                'param_m': param_m,
            })
        response = cs.wait_event(ECsgoGCMsg.EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse, timeout=10)

    except:
        return None

    return response

def Get_Float(paintwear):
    buf = struct.pack('i', paintwear)
    item_float = struct.unpack('f', buf)[0]
    return item_float            
        
def Get_Item_Data(inspect_list, price_list, cs, bg, d):
    total_links = len(inspect_list)
    n = 1
    p = 0
    while (n < total_links):
        cs.launch()
        try:
            current_inspect_link = inspect_list[n]
            price = price_list[p]
            itemcode = current_inspect_link.replace('steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20' ,'').split('A')
            param_m = int(itemcode[0].replace('M',''))
            itemAD = itemcode[1].split('D')
            param_a = int(itemAD[0])
            param_d = int(itemAD[1])

            itemdata = CSGO_Check_Item(param_a, param_d, param_m, cs)
            paintseed = int(itemdata[0].iteminfo.paintseed)
            paintwear = int(itemdata[0].iteminfo.paintwear)
            paintindex = int(itemdata[0].iteminfo.paintindex)
            defindex = str(itemdata[0].iteminfo.defindex)
            skin_name = externalLists.weaponIndex[defindex]
            skin_id = 'ID' + str(paintindex)
            skin_pattern = externalLists.skinIndex[skin_id]
            item_float = float(Get_Float(paintwear))

            if (inspect_list[(n-1)] == 'yes'):
                stattrak = 'yes'
            if (inspect_list[(n-1)] == 'no'):
                stattrak = 'no'
                
            if (defindex == '3'):
                if (paintseed in externalLists.fiveSevenIndex or paintseed in externalLists.fiveSevenT1Index):
                    if (paintseed in externalLists.fiveSevenT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '7'):
                if (paintseed in externalLists.akIndex or paintseed in externalLists.akT1Index):
                    if (paintseed in externalLists.akT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '500'):
                if (paintseed in externalLists.bayonetIndex or paintseed in externalLists.bayonetT1Index):
                    if (paintseed in externalLists.bayonetT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))

                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '515'):
                if (paintseed in externalLists.butterflyIndex or paintseed in externalLists.butterflyT1Index):
                    if (paintseed in externalLists.butterflyT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))                        
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '512'):
                if (paintseed in externalLists.falchionIndex or paintseed in externalLists.falchionT1Index):
                    if (paintseed in externalLists.falchionT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '505'):
                if (paintseed in externalLists.flipIndex or paintseed in externalLists.flipT1Index):
                    if (paintseed in externalLists.flipT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '506'):
                if (paintseed in externalLists.gutIndex or paintseed in externalLists.gutT1Index):
                    if (paintseed in externalLists.gutT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '509'):
                if (paintseed in externalLists.huntsmanIndex or paintseed in externalLists.huntsmanT1Index):
                    if (paintseed in externalLists.huntsmanT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '507'):
                if (paintseed in externalLists.karambitIndex or paintseed in externalLists.karambitT1Index):
                    if (paintseed in externalLists.karambitT1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()
            if (defindex == '508'):
                if (paintseed in externalLists.m9Index or paintseed in externalLists.m9T1Index):
                    if (paintseed in externalLists.m9T1Index):
                        if (stattrak == 'yes'):
                            print("*****TIER ONE*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****TIER ONE*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("T1 %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    else:
                        if (stattrak == 'yes'):
                            print("*****          Stattrak %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("Stattrak %s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                        else:
                            print("*****          %s %s %s %s $%s %s" % (skin_name, skin_pattern, item_float, paintseed, price, current_inspect_link))
                            info = ("%s %s %s $%s %s %s" % (skin_name, skin_pattern, item_float, price, paintseed, current_inspect_link))
                    d.execute("INSERT INTO bluegemTable(info) VALUES (?)", (info,))
                    bg.commit()

            gevent.sleep(1)   
            n += 2
            p += 1
        except:
            print("Retrying item")
            gevent.sleep(5)
                    
def CSGO_Check_Item(param_a, param_d, param_m, cs):
    try:
        cs.send(ECsgoGCMsg.EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockRequest,
            {
                'param_s': 0,
                'param_a': param_a,
                'param_d': param_d,
                'param_m': param_m,
            })
        response = cs.wait_event(ECsgoGCMsg.EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse, timeout=10)

    except:
        return None

    return response

def Get_Float(paintwear):
    buf = struct.pack('i', paintwear)
    item_float = struct.unpack('f', buf)[0]
    return item_float

def Start():
    once = 0
    while True:
        if (once == 0):
            client = SteamClient()
            cs = CSGOClient(client)
            @client.on('logged_on')
            def start_csgo():
                cs.launch()
            @cs.on('ready')
            def gc_ready():
                pass
            client.cli_login()
            print("Waiting 10 seconds for CSGO to start")
            print("")
            gevent.sleep(10)
        once += 1
            
        db = sqlite3.connect('database.db')
        c = db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS inspectsTable(inspects TEXT)')
        c.execute('SELECT * FROM inspectsTable')
        alreadyHave = []
        for row in c.fetchall():
            inspectlink = row[0]
            alreadyHave.append(inspectlink)
        inspect_list = []
        price_list = []
        n = 0
        fail = 0
        while(n < len(externalLists.marketIndex)):
            cs.launch()
            current_market_link = externalLists.marketIndex[n] 
            inspect_price_temp = Get_Inspects(current_market_link, alreadyHave, db, c, fail)
            if (len(inspect_price_temp) == 2 or inspect_price_temp[0] == 'none'):
                if (inspect_price_temp[0] == 'none'):
                    n += 1
                else:
                    inspect_list = inspect_list + inspect_price_temp[0]
                    price_list = price_list + inspect_price_temp[1]
                    n += 1
            if (inspect_price_temp[0] == 'fail'):
                print("Retrying %s waiting 30 seconds..." % current_market_link)
                gevent.sleep(30)
                
        c.close()
        db.close()

        print("")
        
        
        bg = sqlite3.connect('bluegem.db')
        d = bg.cursor()
        d.execute('CREATE TABLE IF NOT EXISTS bluegemTable(info TEXT)')
        
        Get_Item_Data(inspect_list, price_list, cs, bg, d)
            
        d.close()
        bg.close()

Start()
