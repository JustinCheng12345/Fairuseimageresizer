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
# Justincheng12345, 2013
#
# WTFPL, but please credit if possible. ( You can 'not credit', and there isn't
# a problem.)
#

import os,re,urllib
import pywikibot
import Myopener

class FileResizeBot:
    def __init__(self,local):
        self.local = local
        self.site = pywikibot.getSite()
        self.opener = Myopener.MyOpener()
        # MyOpener is urllib.FancyURLopener to request
        # as data.api doesn't provide action = 'parse'

    def run(self):
        self.imagename = pywikibot.input('Which page to work on?')
        self.nofileimagename = self.imagename.split(':')[-1]
        if (self.imagename.split('.')[-1]) == 'svg':
            pywikibot.output('Svg found:'+self.imagename)
            #svg should never be re-sized
            return
        self.do(self.imagename)

    def do(self,page):
        usepage = self.filelink(page)
        if usepage == None:
            return
        url,size = self.parsetext(usepage)
        self.download(url,size)
        raise ValueError('test')
        if not self.local:
            self.upload()
        # TODO: log for successful upload.

    def parsetext(self,usepage):
        results = pywikibot.data.api.Request(action="parse",
                                             page=usepage.title()
                                             ).submit()["parse"]["text"]["*"]
        pywikibot.output(self.site.lang)
        imagename = urllib.quote(self.nofileimagename.encode('utf8'))
        text = imagename+'" width="'
        regext = ('('+re.escape('//upload.wikimedia.org/wikipedia/'+
                                self.site.lang+'/thumb/')+'\\w{1}/\\w{2}/'+
                  re.escape(imagename)+')/\d*?px-'+re.escape(text)+'(\d*?)\\"')
        match=re.search(regext,results, flags=0)
        return match.group(1),match.group(2)
        # Return directly as there will still be error if cannot catch

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

    def download(self,url,size):
        size = int(size)
        if size+50 < 300:
            size = 300
        else:
            size = size+50
        r = (pywikibot.data.api.Request(action='query',prop='imageinfo',
                                      iiprop='size',titles=self.imagename)
           .submit())
        key = str(r["query"]["pages"].keys()).split("[u'")[1].split("']")[0]
        key = str(r["query"]["pages"].get(key))
        size2 = int(re.search("width': (\\d*?),",key,flags=0).group(1))
        # A bit hacky here, but I can't find a way round.
        pywikibot.output(size)
        pywikibot.output(size2)
        if (size2 <= size):
            raise ValueError("Orginal too small")
        url = ('https:'+url+'/'+str(size)+'px-'+
               urllib.quote(self.imagename.split(':')[-1].encode('utf8')))
        self.localf = rewrite_path+'\\Cache\\'+self.imagename.split(':')[-1]
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
    cat = False
    bot = FileResizeBot(local)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
