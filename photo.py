#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
>  REWRITE  <
Alpha script: CHECK your uploads.
"""

"""
This script is used for re-upload a smaller fair use image for fulfilling
requirnment of fair use.
"""
#
# (C) Pywikipedia bot team, 2006-2011
# (C) Justincheng12345, 2013
#
# Distributed under the terms of the MIT license.
#

import os,re,urllib
import pywikibot
import simplejson,Myopener

class FileResizeBot:
    def __init__(self,local):
        self.local = local
        self.site = pywikibot.getSite()
        self.opener = Myopener.MyOpener()
        # MyOpener is urllib.FancyURLopener to request
        # as data.api doesn't provide action = 'parse'

    def run(self):
        self.pagename = pywikibot.input('Which page to work on?')
        if (self.pagename.split('.')[-1]) == 'svg':
            pywikibot.output('Svg found:'+self.pagename)
            #svg should never be re-sized
            return
        self.do(self.pagename)

    def do(self,page):
        usepage = self.filelink(page)
        if usepage == None:
            return
        pagename = pywikibot.Page(usepage)
        lbltitle = pagename.title(asUrl=True)
        url,size = self.parsetext(lbltitle)
        self.download(url,size,lbltitle)
        if not self.local:
            self.upload()
        # TODO: log for successful upload.

    def parsetext(self,lbltitle):
        results = self.doitmyself(1,lbltitle)
        text2 = '//upload.wikimedia.org/wikipedia/zh/thumb/'
        # TODO: zh -> user-config.mylang
        title = self.pagename.split(':')[-1]
        text = title+'" width="'
        regext = ('('+re.escape(text2)+'\\w{1}/\\w{2}/'+re.escape(title)+
                  ')/\d*?px-'+re.escape(text)+'(\d*?)\\"')
        match=re.search(regext,results, flags=0)
        if match:
            return match.group(1),match.group(2)
        else:
            ## FIXME:
            # I don't remember why I should put this here, but this help catch
            # more results. However, unicode-encoded words are still not catched
            # and I don't know why....
            pywikibot.output('a')
            text = lbltitle+'.'+self.pagename.split('.')[-1]+'" width="'
            regext = ('('+re.escape(text2)+'\\w{1}/\\w{2}/'+re.escape(lbltitle)+
                      ')/\d*?px-'+re.escape(text)+'(\d*?)\\"')
            #FIXME Cannot do with others
            pywikibot.output(regext)
            match=re.search(regext,results, flags=0)
            if match:
                return match.group(1),match.group(2)

    def filelink(self,page):
        fileLinksPage = pywikibot.ImagePage(self.site,page)
        a = 0
        for page in pywikibot.pagegenerators.FileLinksGenerator(fileLinksPage):
            a = a+1
        if a>1:
            pywikibot.output('More than one page')
        else:
            return page
        # A fair use image should not be use multiple times.

    def doitmyself(self,time,lbltitle):
        if time == 1:
            url = ('https://zh.wikipedia.org/w/api.php?action=parse&format=jso'+
                   'n&page='+lbltitle)
        else:
            url = ('https://zh.wikipedia.org/w/api.php?action=query&prop=image'+
                   'info&format=json&iiprop=size&titles='+self.pagename)
        pywikibot.output(url)
        result = self.opener.open(url)
        json = simplejson.loads(result.read())
        if time == 1:
            return json["parse"]["text"]["*"]
        else:
            result = json["query"]["pages"]["436757"]["imageinfo"][0]
        result = str(result)
        result = re.search("width': (\\d*?),",result,flags=0).group(1)
        return result
        

    def download(self,url,size,lbltitle):
        size = int(size)
        if size+50 < 300:
            size = 300
        else:
            size = size+50
        if (int(self.doitmyself(0,lbltitle)) <= size):
            raise ValueError("Orginal too small")
        url = 'https:'+url+'/'+str(size)+'px-'+self.pagename.split(':')[-1]
        self.localf = rewrite_path+'\\Cache\\'+self.pagename.split(':')[-1]
        # This should work with using pwb.py or else state it yourself
        self.opener.retrieve(url,self.localf)

    def upload(self):
        filename = os.path.basename(self.localf)
        imagepage = pywikibot.ImagePage(self.site, filename)
        imagepage.text = u'合理使用，降低解像度'
        # TODO: Use i18n
        site = pywikibot.Site()
        try:
            site.upload(imagepage, source_filename=self.localf,
                        ignore_warnings=True)
            # ignore_warnings=True or error:'file exist'
        except Exception, e:
            pywikibot.error("Upload error: ", exc_info=True)

        else:
            # No warning, upload complete.
            # Lazy to catch all errores
            pywikibot.output(u"Upload successful.")     

def main():
    local = False
    bot = FileResizeBot(local)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
