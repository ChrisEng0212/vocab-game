import json
from pprint import pprint


string = 'WPE.json'

with open (string, "r") as f:
        jload = json.load(f) 

newDict = {}

count = 1
for key in jload:
    for part in jload[key]:
        for q in jload[key][part]:
            try:            
                if len(jload[key][part][q]['d']) > 1:
                    newDict[count] = [jload[key][part][q]['w'], jload[key][part][q]['d']]
                    count +=1
            except:
                print('No "d" key')


with open('WPPEQs.json', 'w') as outfile:
    json.dump(newDict, outfile)


