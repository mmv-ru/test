#!pyton

import os

WorkPath = """E:\\MMV\\testgit\\test"""
FileName = """lst_3372.htm"""
LogName = """Log.txt"""

FileD=open(WorkPath + os.sep + FileName, 'rb')
FileLog=open(WorkPath + os.sep + LogName, 'wb')

import codecs, sys
__, __, reader, __ = codecs.lookup("cp1251") 
encoder, __, __, writer = codecs.lookup("cp1251") 
oemout = writer(FileLog) 
ansiin = reader(FileD) 

Page=FileD.read()

oemout.write('Начали...\n')

import htmllib, formatter
import re
from operator import truth
import string

#pattern1='П'
TestString='Предыдущий лист'
#print truth(re.search(pattern1, TestString))
Search_NotSpace=re.compile('\S')
Search_PastRef=re.compile('Предыдущий ли', re.LOCALE | re.MULTILINE | re.UNICODE)

class FKParser(htmllib.HTMLParser):
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.Posts = []
        self.CPost = {}
        self.CurrentHref = None
        self.PastRef = None
        self.State = 0

    def handle_tag(self, tag, open_type, metod, attrs):
        pass
        
    def handle_starttag(self, tag, metod, attrs):
        htmllib.HTMLParser.handle_starttag(self, tag, metod, attrs)
        print "Encountered the beginning of a %s tag" % tag
        if   self.State==2:
            if   tag=='table':
                self.State=3
#        elif self.State==3:
        
        elif self.State==4:
            if   tag=='table':
                self.State=5

    def handle_endtag(self, tag, metod):
        htmllib.HTMLParser.handle_endtag(self, tag, metod)
        print "Enountered the end of a %s tag" % tag
        if   self.State==2:
            pass
        elif self.State==3:
            if   tag=='table':
                self.State=4
        elif self.State==4:
            self.State=5
        
    def anchor_bgn(self, href, name, type):
        if not(href==None):
            self.CurrentHref=href
            print >>FileLog,  'New Href - ', self.CurrentHref
        if not(name==None or name==''):
            self.CurrentAName=name
            print >>FileLog,  'New AName - ', self.CurrentAName
            if re.match(r'\d', self.CurrentAName):
                if self.State < 2 :
                    self.State = 2
                    self.CPost['PostID'] = name
                    print >>FileLog, '  PostID = ', self.CPost['PostID']
                else:
                    print >>FileLog, '                   Unhandled State back !!!!!!!!! '
        htmllib.HTMLParser.anchor_bgn(self, href, name, type)
    def anchor_end(self):
        self.CurrentHref=None
        #htmllib.HTMLParser.anchor_end(self)

    def start_td(self, attributes):
        print >>FileLog,  '                <TD>'
    def end_td(self):
        print >>FileLog,  '                </TD>'

    def start_tr(self, attributes):
        print >>FileLog,  '                <TR>'
    def end_tr(self):
        print >>FileLog,  '                </TR>'
    
    def start_table(self, attributes):
        print >>FileLog,  '                <TABLE>'
    def end_table(self):
        print >>FileLog,  '                </TABLE>'
    
    def do_br(self, attributes):
        print >>FileLog,  '<BR>'
        
    def handle_data(self, data):
        if (truth(Search_PastRef.search(data)) and \
           not(self.CurrentHref==None or self.CurrentHref=='')):
            self.PastRef=self.CurrentHref
            print 'PastRef = ', self.PastRef
        if truth(Search_NotSpace.match(data)):
#            if self.State>
#        if not(data=='\r\n'):
            print >>FileLog, '       БЛОК ТЕКСТА\n'
#            print >>FileLog,  'Match? - ', truth(Search2.search(data))
#            print >>FileLog, 'Match? - ', string.find(data, 'П')
#            ED=encoder(data, 'replace')[0]
            ED=data
            print >>FileLog, ED
#            for c in ED: print >>FileLog, hex(ord(c)),
#            print >>FileLog

#            for c in u'П': print >>FileLog, hex(ord(c)),
#            print >>FileLog
        htmllib.HTMLParser.handle_data(self, data)
#            oemout.write(data)
    pass

Frm=formatter.NullFormatter()
FP=FKParser(Frm)
FP.feed(Page)
FP.close()
