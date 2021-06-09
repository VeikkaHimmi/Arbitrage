import json
import requests
import pymongo
import config #secret keys

#---------------------------------------------------------------#
# getCurrencyPairs() extracts exhange rates between currencies
# exhangerate API only provides snapshot of current rates, buy/sell amount
# on a rate could be used to create an Maxinum flow problem between
# currencies, where the buy/sell amount presents maxinum flow on one rate(or edge)
# -> multiple edges between currencies
#---------------------------------------------------------------#
def getCurrencyPairs():
    
    print("start getCurrencyPairs");

    tickers = tickersFromFile(); #extracts used currency tickers from json.file

    jsonList = [];

    for ticker in tickers: #extracts rates between tickers from exhangerate API
        currencyList = [];

        response = requests.get("https://api.exchangerate.host/latest?base="+ticker);
        data = response.json();

        currencyList.append(data['date']);
        currencyList.append(data['base']);
        currencyList.append(data['rates']);
        
        jsonList.append(currencyList);
        #sendToMongo(data);
        
    saveToFile('pairlist.json',jsonList);
    
    print("stop getCurrencyPairs");

    
def saveToFile(file,data):
    
    with open(file,'w') as outfile:
        
        json.dump(data,outfile);


def tickersFromFile():
    tickerlist = [];

    with open ('currencylist.json') as file:
        data = json.load(file);
        
        for ticker in data['symbols']:
            tickerlist.append(ticker);
            
    return tickerlist;

def sendToMongo(data):

    client = pymongo.MongoClient(config.server);
    db = client[config.server_client];
    collection = db[config.server_db_pair];

    add = {
        'date' : data['date'],
        'base' : data['base'],
        'rates' : data['rates']
    }

    x = collection.insert_one(add);

getCurrencyPairs();