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
# Justincheng12345, 2013
#
# WTFPL, but please credit if possible. ( You can 'not credit', and there isn't
# a problem.)
#

import os, re, urllib, codecs
import pywikibot

class MyOpener(urllib.FancyURLopener):
    version = 'User:JC1-bot python code for those not provided in pywikibot.'

class FileResizeBot:
    def __init__(self, local, gen, prer):
        self.local = local
        self.prer = prer
        self.generator = gen
        self.site = pywikibot.getSite()
        self.opener = MyOpener()
        self.pagelist = []

    def run(self):
        if self.generator:
            for page in self.generator:
                self.run2(page)
        else:
            page = pywikibot.input('Which image to work on?')
            self.run2(page)

    def run2(self, page):
        sinp = False
        if type(page) == unicode:
            sinp = True
        else:
            page = page.title()
        imagename = page.split('.')[-1]
        if imagename == 'svg' or imagename == 'ogg':
            pywikibot.output('\03{green}Unaccepted File Extension\03{default}')
            #svg should never be re-sized
            return
        self.do(page, sinp)

    def do(self, page, sinp):
        self.pagelist.append(page)
        if len(self.pagelist) == 50 or sinp:
            pywikibot.output('Getting page(s).')
            r = self.imageinfo('|'.join(self.pagelist))
            for key in r["query"]["pages"]:
                pagename = r["query"]["pages"][key]["title"]
                pywikibot.output('\03{lightpurple}Start processing '+pagename)
                usepage = self.filelink(pagename)
                if usepage == None:
                    continue
                pywikibot.output('\03{default}Start parsing '+usepage.title())
                url, size = self.parsetext(usepage, pagename)
                if size:
                    size2 = r["query"]["pages"][key]["imageinfo"][0]["width"]
                    Suc, size = self.sizecheck(size, size2)
                    if not Suc:
                        continue
                else:
                    continue
                if not self.prer:
                    pywikibot.output('Start downloading image')
                    localf = self.download(url, size, pagename)
                    if not self.local:
                        pywikibot.output('Start uploading image')
                    #    self.upload(localf, pagename)
                if self.prer:
                    pywikibot.output('Start logging.')
                    f = codecs.open(pywikibot.config.datafilepath('b.txt'),'a',
                                    'utf-8')
                    f.write(u"# [[%s]]" % (page))
                    f.write("\n")
                    f.close()
            self.pagelist = []

    def parsetext(self, usepage, pagename):
        results = pywikibot.data.api.Request(action="parse",
                                             page=usepage.title()
                                             ).submit()["parse"]["text"]["*"]
        imagename = urllib.quote(pagename.split(':')[-1].encode('utf8'))
        imagename = imagename.replace(u'%20', u'_')
        text = imagename+'" width="'
        regext = ('('+re.escape('//upload.wikimedia.org/wikipedia/'+
                                self.site.lang+'/thumb/')+'\\w{1}/\\w{2}/'+
                  re.escape(imagename)+')/\d*?px-'+re.escape(text)+'(\d*?)\\"')
        # if the thumb is larger than the orginal image, then the address
        # will not include /thumb/, and hence no match will be given. As no
        # should be re-sized, return None
        match = re.search(regext,results, flags=0)
        if match:
            return match.group(1), int(match.group(2))
        else:
            pywikibot.output('\03{green}Regex cannot catch result, it is '+
                             'possible that usage size is larger than or the'+
                             'same with the orginal.')
            return None, None

    def filelink(self, page):
        fileLinksPage = pywikibot.ImagePage(self.site, page)
        a = 0
        for usepage in pywikibot.pagegenerators.FileLinksGenerator(
            fileLinksPage):
            a = a + 1
        if a > 1:
            pywikibot.output('\03{green}The file is used multiple times.')
        else:
            try:
                return usepage
            except:
                return None
        # A fair use image should not be use multiple times.

    def download(self, url, size, pagename):
        page = pagename.split(':')[-1]
        url = 'https:'+url+'/'+str(size)+'px-'+urllib.quote(page.encode('utf8'))
        url = url.replace(u'%20', u'_')
        localf = pywikibot.config.base_dir+'\\Cache\\'+page
        self.opener.retrieve(url, localf)
        return localf
        # Well, this doesn't work on tools lab.

    def imageinfo(self, name):
        r = (pywikibot.data.api.Request(action='query', prop='imageinfo',
                                        iiprop='size', titles=name).submit())
        return r
    
    def sizecheck(self, size, size2):
        if size + 50 < 300:
            size = 300
        else:
            size = size + 50
        if (size2 <= size) or (size2-size<50):
            pywikibot.output("\03{green}Orginal image is too small to"+
                             "proceed\03{default}")
            return False, 0
        return True, size

    def upload(self, localf, pagename):
        imagepage = pywikibot.ImagePage(self.site, pagename)
        imagepage.text = u'合理使用，降低解像度'
        # TODO: Use i18n
        site = pywikibot.Site()
        try:
            site.upload(imagepage, source_filename=localf,ignore_warnings=True)
            # ignore_warnings=True or error:'file exist'
        except Exception:
            pywikibot.error("Upload error: ", exc_info=True)
        else:
            # No warning, upload complete.
            # Lazy to catch all errores
            pywikibot.output(u"Upload successful.")
            os.remove(self.localf)

def main(*args):
    local = False
    prer = False
    gen = None
    preloadingGen = None
    genFactory = pywikibot.pagegenerators.GeneratorFactory()
    for arg in pywikibot.handleArgs(*args):
        if genFactory.handleArg(arg):
            continue
        if arg == '-local':
            local = True
        elif arg == '-prer':
            prer = True
    gen = genFactory.getCombinedGenerator()
    #if gen:
    #    preloadingGen = pywikibot.pagegenerators.PreloadingGenerator(gen)
    # Do not preload as not processing on the image page itself, will preload
    # later.
    bot = FileResizeBot(local, gen, prer)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
