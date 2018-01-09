
import os
import json
import requests


 
isbn = '0851109519'
response = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:'+ isbn)

data = json.loads(response.content)

# with open('sampleJSON.json', 'r') as Datafile:
# 	data = json.load(Datafile)





# Datajson = response.json()



# json.load(Datajson)


# # jsonData.getJSONArray("kind")
# # #.getJSONObject(0).getString("article")

#print Datajson




#printing out all the required fields 

print data['items'][0]['volumeInfo']['title']
print data['items'][0]['volumeInfo']['subtitle']
print data['items'][0]['volumeInfo']['authors'][0]
print data['items'][0]['volumeInfo']['categories'][0]
print data['items'][0]['volumeInfo']['description']
print data['items'][0]['volumeInfo']['publishedDate']
print data['items'][0]['volumeInfo']['industryIdentifiers']
