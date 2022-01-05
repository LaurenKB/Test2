
"""
Save new chapters of Solo Leveling from 365manga
"""

import requests
import os
# import math
import re
from PIL import Image
from PyPDF2 import PdfFileMerger
from shutil import copyfile
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import urllib

my_referer='https://365manga.com/'
headers = {}
headers['Referer'] = my_referer

storypath='C:/Users/Main/Documents/Books/Solo Leveling/'

fldrs=os.listdir(storypath)
numchaps=len(fldrs)-2

storyurl='https://365manga.com/manga/solo-leveling/'
#storyreq=requests.get(storyurl)
#storyData=storyreq.text
browser = webdriver.Chrome()
browser.get(storyurl)
# userAgent = browser.execute_script("return navigator.userAgent;")
# seleniumCookies= browser.get_cookies()
# cookies = ''
# for cookie in seleniumCookies:
#         cookies += '%s=%s;' % (cookie['name'], cookie['value'])
storyData=browser.page_source


chapListStart=storyData.find('class="main version-chap')
chapListEnd=storyData.find('div id="manga-discussion"')

latestEp=storyData.find('Chapter ',chapListStart,chapListEnd)
latestEp=storyData[latestEp+8:]
endLatestEp=latestEp.find('<')
latestEp=latestEp[0:endLatestEp]
latestEp=int(latestEp)

numToDo=latestEp-numchaps

print("Solo Leveling chaps to do: " + str(numToDo))

chapList=storyData[chapListStart:chapListEnd]
chapsStart=[m.start() for m in re.finditer('wp-manga-chapter',chapList)]
chapsEnd=[m.start() for m in re.finditer('chapter-release-date',chapList)]

for ind in range(numToDo,0,-1):
    chapnum=latestEp-ind+1
    
    chapurl=chapList[chapsStart[ind-1]:chapsEnd[ind-1]]
    chapurlS=chapurl.find('http')
    tempchapurl=chapurl[chapurlS:]
    chapurlE=tempchapurl.find('">')
    chapurl=tempchapurl[:chapurlE]
    
    # chapreq=requests.get(chapurl)
    # chapData=chapreq.text
    browser.get(chapurl)
    chapData=browser.page_source
    
    imgListStart=chapData.find('page-break no-gaps')
    imgListEnd=chapData.find('entry-header footer')
    imgList=chapData[imgListStart:imgListEnd]
    imgsStart=[m.start() for m in re.finditer('src="',imgList)]
    imgsEnd=[m.start() for m in re.finditer('class="wp-manga',imgList)]
    
    chappath=storypath + 'Solo Leveling ' + str(chapnum) + '/'
    os.mkdir(chappath)
    imgpdfs=[]
    
    chapname = 'Chapter ' + str(chapnum) + '.pdf'
    chapfilename=chappath + chapname
    
    if chapnum>=111:
        seasonfile=storypath + 'chapters/Solo Leveling Season 2.pdf'
    else:
        seasonfile=storypath + 'chapters/Solo Leveling Season 1.pdf'
       
    print("imgs to do for chap " + str(chapnum) + ": " + str(len(imgsEnd)))

    for ind2 in range(0,len(imgsEnd)):
        imgurl=imgList[imgsStart[ind2]+6:imgsEnd[ind2]-2]
        filename=chappath + str(ind2+1) + '.jpg'
        filename2=chappath + str(ind2+1) + '.pdf'
        counter=0;done=False #will try 10 times 
        while counter<10 and not done:
            try:
                r = requests.get(imgurl, headers=headers, allow_redirects=False)
                with open(filename, 'wb') as fh:
                    fh.write(r.content)
                # urllib.request.urlretrieve(imgurl,filename)
                image=Image.open(filename)
                image1 = image.convert('RGB')
                image1.save(filename2)
                imgpdfs.append(filename2)
                done=True
            except:
                counter+=1
        
    print("Merging pdfs to make chapter")
    
    chap_merger=PdfFileMerger()
    for pdf in imgpdfs:
        chap_merger.append(pdf)    
    chap_merger.write(chapfilename)
    chap_merger.close()
    
    copyfile(chapfilename,storypath + 'chapters/' + chapname)
    
    
    print("Adding chapter to season file")
    
    if chapnum == 1 or chapnum == 111:
        copyfile(chapfilename,seasonfile)
    else:
        tempfile=storypath + 'chapters/temp.pdf'
        copyfile(seasonfile,tempfile)
        
        story_merger=PdfFileMerger()
        story_merger.append(tempfile)
        story_merger.append(chapfilename)
        story_merger.write(seasonfile)
        story_merger.close()
        
        os.remove(tempfile)
    
    print("Adding chapter to series file")
    
    if chapnum==1:
        seriesfile=storypath + 'chapters/Solo Leveling.pdf'
        copyfile(chapfilename,seriesfile)
    else:
        seriesfile='C:/Users/Main/Documents/Books/Solo Leveling/chapters/Solo Leveling.pdf'
        seriestempfile=storypath + 'chapters/temp.pdf'
        copyfile(seriesfile,seriestempfile)
    
        story_merger=PdfFileMerger()
        story_merger.append(seriestempfile)
        story_merger.append(chapfilename)
        story_merger.write(seriesfile)
        story_merger.close()
        
        os.remove(seriestempfile)
        
browser.close()