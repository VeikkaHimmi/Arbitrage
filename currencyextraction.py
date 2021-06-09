import json
import requests
import pymongo
import config #hidden keys

#---------------------------------------------------------------#
# getCurrencyLabels() extracts available tickers from API and saves
# them to currencylist.json
#---------------------------------------------------------------#
def getCurrencyLabels():
    print("Start getCurrencies");
    
    response = requests.get("https://api.exchangerate.host/symbols");

    data = response.json();

    print(data);
    
    saveToFile('currencylist.json',data); #function for saving tickers as json file
    #sendToMongo(data); #function to send tickers to mongoDB

    print("Done getCurrencies");

def saveToFile(file,data):

    with open(file,'w') as outfile:
        json.dump(data,outfile);

def sendToMongo(data):

    #Or just save to a file..
    client = pymongo.MongoClient(config.server);
    db = client[config.server_client];
    collection = db[config.server_db_currency];

    
    add = {
        "symbols" : data['symbols']
    }

    x = collection.insert_one(add);


getCurrencyLabels();
    
