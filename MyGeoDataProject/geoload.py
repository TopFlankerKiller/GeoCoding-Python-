import urllib
import sqlite3
import json
import time
import ssl

serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"
scontext = None

conn = sqlite3.connect('mygeodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (destination TEXT, geodata TEXT)''') #This is the table with my destinations 

fh = open("destinations.data")
count = 0

for line in fh:
    if count > 200 : break
    destination = line.strip()
    print ''
    cur.execute("SELECT geodata FROM Locations WHERE destination= ?", (buffer(destination), ))
    
    try:
        data = cur.fetchone()[0]
        print "Found in database ",destination
        continue
    except:
        pass
    
    print 'Resolving', destination
    url = serviceurl + urllib.urlencode({"sensor":"false", "address": destination})
    print 'Retrieving', url
    uh = urllib.urlopen(url)
    data = uh.read()
    print 'Retrieved',len(data),'characters',data[:20].replace('\n',' ')
    count = count + 1
    try: 
        js = json.loads(str(data))
        # print js  # We print in case unicode causes an error
    except: 
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print '==== Failure To Retrieve ===='
        print data
        break

    cur.execute('''INSERT INTO Locations (destination, geodata) 
            VALUES ( ?, ? )''', ( buffer(destination),buffer(data) ) )
    conn.commit() 
    time.sleep(1)

print "Run geodump.py to read the data from the database so you can visualize it on a map."
