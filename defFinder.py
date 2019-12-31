import json
from pprint import pprint


string = 'FRD.json'

with open (string, "r") as f:
        jload = json.load(f) 

newDict = {}

count = 1
for key in jload:
    for part in jload[key]:
        for q in jload[key][part]:
            if len(jload[key][part][q]['d']) > 1:
                newDict[count] = [jload[key][part][q]['w'], jload[key][part][q]['d']]
                count +=1


with open('FRDQs.json', 'w') as outfile:
    json.dump(newDict, outfile)


