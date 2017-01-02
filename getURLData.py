import requests
import bs4
from bs4 import BeautifulSoup
from urlparse import urlparse
import csv
import urllib2
import re
import nltk
import wordsegment

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

print('\n Output from an iterable object created from the csv file')
arrayofdata=[]
with open('1.csv', 'rb') as mycsvfile:
    thedata = csv.reader(mycsvfile)
    for row in thedata:
        print(row[0]+"\t \t"+row[1])
        #url = row[0]
        url = "http://elgintoyota.com"
        try:
            r = requests.get(url,timeout=5)
            print "The status code" ,r.status_code
            if r.status_code != 200 :
                continue
        except Exception, e:
            print e
            continue                
        html = BeautifulSoup(r.content, "html.parser")
        for tag in html.find_all("meta"):
            print  tag.get("name", None)
            print  tag.get("content", None)
        title = html.find("meta",  property="og:title")
        author = html.find("meta",  property="author")
        keywords = html.find("meta",  property="keywords")
        print(title["content"] if title else "No meta title given")
        print(author["content"] if author else "No meta author given")
        print(keywords["content"] if keywords else "No meta keywords given")
        titleContent="No meta title given"
        authorContent="No meta author given"
        keywordsContent="No meta author given"
        if title : titleContent = title["content"] 
        if author : authorContent = author["content"]
        if keywords : keywordsContent = keywords["content"]
        pattern = re.compile('((http|ftp)s?://.*?)')
        word = 'facebook.com'
        advertiser = ''
        for a in html.find_all('a', {'href': pattern}):  
            print a['href']          
            if word in a['href'] : 
                print 'Facebook check'
                print "Found the URL:", a['href']
                parse_object = urlparse(a['href'])
                print parse_object.path
                advertiser = re.sub('[^\s+a-zA-Z0-9*]|pages', ' ', parse_object.path)
                print advertiser

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
        allWordExceptStopDist = nltk.FreqDist(w.lower() for w in allWords if w.lower() not in stopwords)
        #print allWordExceptStopDist
        #print allWordExceptStopDist.most_common(30)
        commonwords=[]
        for word, count in allWordExceptStopDist.most_common(50):
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
        print row[0],commonwordsCSV,commonwordsrepeatedCSV,row[1],advertiser,titleContent,authorContent,keywordsContent
        arrayofdata.append([row[0],commonwordsCSV,commonwordsrepeatedCSV,row[1],advertiser,titleContent,authorContent,keywordsContent])
with open('1mydata.csv', 'w') as mycsvfile1:
            thedatawriter = csv.writer(mycsvfile1)
            for row in arrayofdata:         
                thedatawriter.writerow(row)     
