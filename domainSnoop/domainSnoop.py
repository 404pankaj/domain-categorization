import requests
import bs4
from bs4 import BeautifulSoup
from urlparse import urlparse
import csv
import urllib2
import re
import nltk
import wordsegment
import json
import ConfigParser
import whois

config = ConfigParser.RawConfigParser()
config.read('ConfigFile.properties')

def get_page_data(page_id,access_token):
    api_endpoint = "https://graph.facebook.com/v2.4/"
    fb_graph_url = api_endpoint+page_id+"?fields=id,category_list,name,likes,location,description,link,global_brand_page_name&access_token="+access_token
    try:
        api_request = urllib2.Request(fb_graph_url)
        api_response = urllib2.urlopen(api_request)
        
        try:
            return json.loads(api_response.read())
        except (ValueError, KeyError, TypeError):
            return "JSON error"

    except IOError, e:
        if hasattr(e, 'code'):
            return e.code
        elif hasattr(e, 'reason'):
            return e.reason

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

print('\n Output from an iterable object created from the csv file')
arrayofdata=[]
with open('domain/domains_00.csv', 'rb') as mycsvfile:
    thedata = csv.reader(mycsvfile)
    for row in thedata:
        #print(row[0]+"\t \t"+row[1])
        url = row[0]
        #url = "http://elgintoyota.com"
        try:
            pattern = re.compile('((http|ftp)s?://.*?)')
            status='NA'
            word = 'facebook.com'
            advertiser = 'NA'
            category='NA'
            iabCategory='NA'
            likes='NA'
            description='NA'
            location='NA'
            commonwordsCSV=''
            r = requests.get(url,timeout=5)
            status=r.status_code
            if r.status_code != 200 :
                arrayofdata.append([row[0],row[1],status,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,'NA'])
                print "Data -------:" + row[0],row[1],status,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,'NA' 
                continue                       
            html = BeautifulSoup(r.content, "html.parser")   
            #titleContent="No meta title given"
            #authorContent="No meta author given"
            #keywordsContent="No meta keywords given"
            #titleName = html.find(attrs={'name':'og:title'}) 
            #authorName = html.find(attrs={'name':'author'}) 
            #keywordsName = html.find(attrs={'name':'keywords'})  
            #if titleName :  print titleName["content"]
            #if authorName : print authorName["content"]
            #if keywordsName : print keywordsName["content"]
              
            #titleProperty = html.find("meta",  property="og:title")
            #authorProperty = html.find("meta",  property="author")
            #keywordsProperty = html.find("meta",  property="keywords")
           
            #if titleName : titleContent = titleName["content"] 
            #if authorName : authorContent = authorName["content"]
            #if keywordsName : keywordsContent = keywordsName["content"]
            #if titleProperty : titleContent = titleProperty["content"] 
            #if authorProperty : authorContent = authorProperty["content"]
            #if keywordsProperty : keywordsContent = keywordsProperty["content"]           
            
            for a in html.find_all('a', {'href': pattern}):  
                #print a['href']          
                if word in a['href'] : 
                    #print 'Facebook check'
                    #print "Found the URL:", a['href']                 
                    parse_object = urlparse(a['href'])
                    #print parse_object.path
                    page_id = parse_object.path.encode('utf-8') # username or id
                    page_id=page_id.replace('/','')
                    token = config.get('FB', 'fb.token');
                    page_data = get_page_data(page_id,token)               
                    #print page_data
                    #print "Page category:"+ page_data['category']
                    #print "Page Name:"+ page_data['name']
                    #print "Likes:"+ str(page_data['likes'])
                    #print "Link:"+ page_data['link']
                    
                    #advertiser = re.sub('[^\s+a-zA-Z0-9*]|pages', ' ', parse_object.path)
                    #print "Advertiser :"+advertiser
                    try:
                        if page_data['global_brand_page_name'] : advertiser=page_data['global_brand_page_name']
                        if page_data['category_list'] :
                            catdata=[ x['name'] for x in page_data['category_list']]
                            iabdata=[config.get('FB-IAB-MAP', x['name'] ) for x in page_data['category_list']]
                            iabCategory=" ".join(str(y) for y in iabdata)
                            category=" ".join(str(y) for y in catdata)
                            print iabCategory + ":" + category
                        if page_data['likes'] : likes=page_data['likes']
                        #print "likes :",likes
                        if page_data['description'] : description=page_data['description']
                        #print "description :",description
                        if page_data['location']['country'] : location=page_data['location']['country']
                        #print "location :",location                    
                        #print "Page location -------:"+ page_data['location.country']
                    except Exception, e:
                        print e
                        continue 

            # kill all script and style elements
            for script in html(["script", "style"]):
                script.extract()    # rip it out
            text = html.get_text()
            text = re.sub('[^\s+a-zA-Z*]', ' ', text)
            #print text.encode('utf-8')
            # get text
            #text = soup.get_text()
            allWords = nltk.wordpunct_tokenize(text.encode('utf-8'))
            #print allWords
            allWordDist = nltk.FreqDist(w.lower() for w in allWords)
            stopwords = nltk.corpus.stopwords.words('english')
            http_stopwords = open('repetitive.txt').read().splitlines()
            stopwords += http_stopwords
            allWordExceptStopDist = nltk.FreqDist(w.lower() for w in allWords if w.lower() not in stopwords)

            #print allWordExceptStopDist
            #print allWordExceptStopDist.most_common(30)
            commonwords=[]
            for word, count in allWordExceptStopDist.most_common(200):
                if len(word) < 3 :
                    continue
                commonwords.append(word);
                #print("{0}: {1}".format(word, count))
            #print commonwords
            commonwordsrepeated=[]
            #print "Word list",allWordExceptStopDist
            #print "common word list",commonwords
            for word in allWords:
                if word in commonwords:                
                    commonwordsrepeated.append(word);
            
            #stuff = ' '.join(w for w in allWordExceptStopDist if w.lower() in commonwords)
            #print "The commonwordsrepeated is", commonwordsrepeated
            commonwordsCSV = ",".join(commonwords)
            commonwordsrepeatedCSV = ",".join(commonwordsrepeated)
            #print commonwordsCSV
            #test = [('duck', 1), ('duck', 2), ('goose', 0), ('goose', 3)]
            #print test.most_common(1)    
            # break into lines and remove leading and trailing space on each
            #lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            #text = " ".join(chunk for chunk in chunks if chunk)
            #text = re.sub('[^\s+a-zA-Z-_*.]', ' ', text)
            #commonwordsCSV = commonwordsCSV.encode('utf-8')
            #print row[0],commonwordsCSV,commonwordsrepeatedCSV,row[1],advertiser.encode('utf-8'),category.encode('utf-8')
            #arrayofdata.append([row[0],commonwordsCSV,commonwordsrepeatedCSV,row[1],advertiser.encode('utf-8'),category.encode('utf-8')])
            
            arrayofdata.append([row[0],row[1],status,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,commonwordsCSV])
            print "Data -------:" + row[0],row[1],status,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,commonwordsCSV 
        except Exception, e:
            print e
            arrayofdata.append([row[0],row[1],e.message,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,commonwordsCSV])
            print "Data -------:" + row[0],row[1],e.message,advertiser.encode('utf-8'),category.encode('utf-8'),iabCategory,location,commonwordsCSV 
            continue    
with open('domain/data00.csv', 'w') as mycsvfile1:
            thedatawriter = csv.writer(mycsvfile1)
            for row in arrayofdata:         
                thedatawriter.writerow(row)     

