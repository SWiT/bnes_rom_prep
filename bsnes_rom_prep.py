import os
import gzip
import urllib
import bs4
import re
import Image
import StringIO

romspath = "/media/sf_SNES/rom"
imagespath = "/media/sf_SNES/images"
inputxmlfile = "default_games.xml"
outputxmlfile = "/media/sf_SNES/games.xml"
sneslisturl = "http://en.wikipedia.org/wiki/List_of_Super_Nintendo_Entertainment_System_games"
coverspath = "/media/sf_SNES/SNES Shrunken Spine (762)/USA (601 + 65 Alts)"

def wordlist_remove(wordlist, val):
    try:
        wordlist.remove(val)
    except ValueError:
        pass
    return wordlist

def escape(s):
    if s == None:
        return ""
    htmlCodes = (('&', '&amp;'),('<', '&lt;'),('>', '&gt;'),('"', '&quot;'),("'", '&#39;'))
    for code in htmlCodes:
        s = s.replace(code[0], code[1])
    return s  
    
response = urllib.urlopen(sneslisturl)
sneslistsoup = bs4.BeautifulSoup(response.read())
rows = sneslistsoup.select('table.sortable tr')

pattern = re.compile("\(.+\)|\[.+\]|[#!,]|SNES|- |.smc|.gz", re.IGNORECASE)    

fpxml = open(inputxmlfile, 'r')
inputxml = fpxml.read()
fpxml.close()

outputxml = inputxml[0:inputxml.index("<snes>")]
outputxml += "<snes>\n"
roms = os.listdir(romspath)
roms.sort()
numroms = 0
for rom in roms:
    if rom[-4:].lower()==".smc": #uncompressed rom file, gzip it
        if not os.path.isfile(romspath+'/'+rom+'.gz'):
            print "gzipping "+rom+"...\n"
            f_in = open(romspaths+'/'+rom, 'rb')
            f_out = gzip.open(romspath+'/'+rom+'.gz', 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            os.remove(rom)  #delete the uncompressed rom
            rom += ".gz"
    
    title = pattern.sub("",rom).strip()
    wordlist = title.replace("-"," ").split()
    wordlist = wordlist_remove(wordlist,"The")
    wordlist = wordlist_remove(wordlist,"the")
    wordlist = wordlist_remove(wordlist,"of")
    if "II" in wordlist: wordlist.append("2")
    if "III" in wordlist: wordlist.append("3")
    
    mostwords = 0
    foundrow = None
    foundatag = None
    year = ""
    genre = ""
    imgfile = ""
    for row in rows:
        rowcount  = 0;
        cells = row.find_all("td")
        if len(cells) > 0:
            itags = cells[0].find_all('i')
            t = ""
            atag = None
            for itag in itags:
                a = itag.find('a')
                if a:
                    atag = a
                    t += " "+a.text.lower()
                else:
                    t += " "+itag.text.lower()
            for w in wordlist:
                if w.lower() in t:
                    rowcount += 1
                elif w.lower() in t.replace(" ",""):
                    rowcount += 1
                elif w.lower() in t.replace("-",""):
                    rowcount += 1
            if rowcount > mostwords:
                mostwords = rowcount
                foundrow = row
                foundatag = atag
    
    print "\n"        
    if foundrow != None:
        #print foundatag.get("href")
        description = title
        if foundatag != None:
            if description != foundatag.string:
                description += " | "+foundatag.string
        cells = foundrow.find_all("td")
        if len(cells) >= 2:
            year = cells[1].string.split()
            if len(year) > 1:
                year = year[2]
            else:
                year = year[0]
        if len(cells) >= 6:
            genre = cells[5].string
    else:
        description = title+" !!!"
        print "!!!", foundatag, wordlist
    
    #print rom
    print title
    print description.encode('utf-8')    
    print year
    if genre != "": print genre
    if foundatag != None: 
        #Find the cover art or screen shot image
        gameurl = "http://en.wikipedia.org"+foundatag.get("href")
        print gameurl
        imgfile = imagespath+"/"+rom+".png"
        if not os.path.isfile(imgfile):
            #No image, try to download and resize one.
            gamesoup = bs4.BeautifulSoup(urllib.urlopen(gameurl).read())
            imgs = gamesoup.select("table.infobox a.image img")
            if len(imgs)>0:
                imgurl = "http:"+imgs[0].get("src")
                print imgurl
                imgdata = StringIO.StringIO(urllib.urlopen(imgurl).read())
                img = Image.open(imgdata)
                img.thumbnail((200,145))
                img.save(imgfile)
        

    outputxml += "  <game>\n"
    outputxml += "    <title>"+escape(title)+"</title>\n"
    outputxml += "    <rom>"+escape(rom)+"</rom>\n"
    if year!="":
        outputxml += "    <year>"+year+"</year>\n"
    if genre!="":
        outputxml += "    <genre>"+escape(genre)+"</genre>\n"
    if os.path.isfile(imgfile):
        print rom+".png"
        outputxml += "    <image>"+rom+".png</image>\n"
    if len(description) >= 43:
        el1 = description[0:43].rfind(' ')
        outputxml += "    <text>"+escape(description[0:el1])+"</text>\n"
        outputxml += "    <text>"+escape(description[el1+1:])+"</text>\n"
    else:
        outputxml += "    <text>"+escape(description[0:43])+"</text>\n"
    outputxml += "  </game>\n"
    
    numroms += 1
    #if numroms >= 10: #only do some of the files while testing
    #    break;

outputxml += "</snes>\n"    
fpoutput = open(outputxmlfile, "w")
fpoutput.write(outputxml.encode('utf-8'))
fpoutput.close()    
    
print "\n"+str(numroms)+" roms found.\n"   
    
