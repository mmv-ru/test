#!pyton
# -*- coding: cp1251 -*-
# Tested on Python Release 2.3 Win32

import os

WorkPath = """E:\MMV\pt"""
FileName = """lst_3372.htm"""
LogName = """Log.txt"""

from types import *

FileD=open(WorkPath + os.sep + FileName, 'rb')
FileLog=open(WorkPath + os.sep + LogName, 'wb')

import codecs, sys
__, __, reader, __ = codecs.lookup("cp1251") 
encoder, __, __, writer = codecs.lookup("cp1251") 
oemout = writer(FileLog) 
ansiin = reader(FileD) 

Page=FileD.read()

#oemout.write('Начали...\n')

import htmllib, formatter
import re
from operator import truth
import string

flags=re.LOCALE | re.MULTILINE | re.UNICODE | re.VERBOSE | re.DOTALL | re.IGNORECASE

#print >>FileLog, '\n         А по русски?\n'

PagePos=0

#1
re1=re.compile('''
    .*?<table[^>]*?>
    .*?<tr[^>]*?>
    .*?<td[^>]*?>
    (.*?<a\ href="(?P<PrevRef>lst_[0-9]*\.htm)">.*?(Предыдущий).*?</a>|)
    .*?<td[^>]*?>
    .*?\d{1,2}\ \S*?\ \d{2,4}\ -\ \d{1,2}\ \S*?\ \d{2,4}.*?  # Date - Date
    .*?<td[^>]*?>
    (.*?<a\ href="(?P<NextRef>lst_[0-9]*\.htm)">.*?(Следующий).*?</a>|)
    .*?</table>
                    ''', flags)
print re1
match1=re1.match(Page, PagePos)
PagePos=match1.end()
print match1.groups()
print >>FileLog, 'Предидущий лист : ' + match1.groupdict('')['PrevRef']
print >>FileLog, 'Следующий лист  : ' + match1.groupdict('')['NextRef']


#2
re2=re.compile('''
    .*?добавить\ новое
                    ''', flags)
match2=re2.match(Page, PagePos)
PagePos=match2.end()
print match2.groups()
print 'forrum Header passed'
print >>FileLog, 'forrum Header passed'

#3 begin repeating part
re3=re.compile('''
    .*?<table[^>]*?>.*?
    <tr[^>]*?>.*?
    <td[^>]*?>.*?
    <font\ size=2[^>]*?>(?P<ReplyOn>.*?)</font>.*?   # Отклик на
    </table>
                    ''', flags)
match3=re3.match(Page, PagePos)
PagePos=match3.end()
print match3.groups()
print >>FileLog
print >>FileLog, 'Отклик на   : ' + match3.group('ReplyOn')

#4
re4=re.compile('''
    .*?<table[^>]*?>
    .*?<tr[^>]*?>
    .*?<td[^>]*?>
    .*?<font[^>]*?>
    .*?&nbsp;<b>(?P<Author>[^<>]*?)</font>   # author
    .*?<td[^>]*?>
    .*?<font[^>]*?>
    .*?(?P<Date>\d{1,2}\ \S*?\ \d{2,4}).*?</font>  # Date
    .*?<td[^>]*?>
    .*?<font[^>]*?>
    .*?(?P<Time>\d{1,2}:\d{2}).*?</font>   #  Time
    .*?<td[^>]*?>
    .*?<font[^>]*?>
    .*?Cообщение\ №\ (?P<MsgID>\d+).*?</font>  # MsgID
    .*?<td[^>]*?>
    .*?<tr[^>]*?>
    .*?<td[^>]*?>
    .*?<font[^>]*?>.*?Тема:.*?</font>
    .*?<td[^>]*?>
    .*?Опусы\ и\ пародии,\ навеянные\ фант\.\ произведениями
    .*?</table>

    .*?<table[^>]*?>
    .*?<tr[^>]*?>
    .*?Заголовок:
    .*?<td[^>]*?>&nbsp;(?P<PostName>.*?)  # Subtopic
    \s*<tr[^>]*?>
    .*?<td[^>]*?>\s*(?P<PostBody>.*?)      # Body
    \s*</table>

    .*?<table[^>]*?>
    .*?<tr[^>]*?>
    .*?<td[^>]*?>
    .*?<a\ href="mailto:(?P<AuthorMail>[^<>]*?)"[^>]*?>.*?</a> # Author e
    .*?<a\ href="http://(?P<AuthorWWW>[^<>]*?)"[^>]*?>.*?</a>

    (?P<Replies>.*?)                       # Возможные Оклики

    .*?<tr[^>]*?>
    .*?</table>
                    ''', flags)

match4=re4.match(Page, PagePos)
PagePos=match4.end()
print >>FileLog, 'Автор       : ' + match4.group('Author')
print >>FileLog, 'Дата        : ' + match4.group('Date') + '  ' + match4.group('Time')
print >>FileLog, 'Сообщение № : ' + match4.group('MsgID')
print >>FileLog
print >>FileLog, 'Топик       : ' + match4.group('PostName')
print >>FileLog
print >>FileLog, match4.group('PostBody')
print >>FileLog
print >>FileLog, 'Mailto      : ' + match4.group('AuthorMail')
print >>FileLog, 'http://     : ' + match4.group('AuthorWWW')
print >>FileLog, 'Отклики     : ' + match4.group('Replies')

# Конец повторяющейся части

print PagePos
print Page[PagePos:PagePos+400]

#pattern1='П'
TestString='Предыдущий лист'
#print truth(re.search(pattern1, TestString))
Search_NotSpace=re.compile('\S')
Search_PastRef=re.compile('Предыдущий ли', re.LOCALE | re.MULTILINE | re.UNICODE)

STARTTAG=1
ENDTAG=2

TestTemplate=[]

class FKParser(htmllib.HTMLParser):
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.Posts = [] #List
        self.CPost = {} #Dictionary
        self.CurrentHref = None
        self.PastRef = None
        self.State = 0

    def handle_tag(self, tag, open_type, metod, attrs):
        if   self.State==2:
            if   tag=='table':
                self.State=3
        elif self.State==3:
            if   tag=='table':
                self.State=4
        elif self.State==4:
            if   tag=='table':
                self.State=5
        
    def handle_starttag(self, tag, metod, attrs):
        print "Encountered the beginning of a %s tag" % tag
        htmllib.HTMLParser.handle_starttag(self, tag, metod, attrs)
        self.handle_tag(tag, STARTTAG, metod, attrs)

    def handle_endtag(self, tag, metod):
        print "Enountered the end of a %s tag" % tag
        htmllib.HTMLParser.handle_endtag(self, tag, metod)
        self.handle_tag(tag, ENDTAG, metod, [])

    def handle_charref(self, ref):
        print >>FileLog, ref

    def handle_entityref(self, ref):
        print >>FileLog, ref
        
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

#FP=FKParser(formatter.NullFormatter())
#FP.feed(Page)
#FP.close()


class HTTemplateParser(htmllib.HTMLParser):
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.Posts = [] #List
        self.CPost = {} #Dictionary
        self.CurrentHref = None
        self.PastRef = None
        self.State = 0

    def handle_tag(self, tag, open_type, attrs):
        if open_type==STARTTAG:
            print >>FileLog, '<%s' % tag ,
            for TParam in attrs: print >>FileLog, ' %s="%s"' % TParam,
            print >>FileLog, '>'
        elif open_type==ENDTAG:
            print >>FileLog, '</%s>' % tag
        pass

    def handle_starttag(self, tag, metod, attrs):
        self.handle_tag(tag, STARTTAG, attrs)
        htmllib.HTMLParser.handle_starttag(self, tag, metod, attrs)

    def handle_endtag(self, tag, metod):
        self.handle_tag(tag, ENDTAG, [])
        htmllib.HTMLParser.handle_endtag(self, tag, metod)
       
    def unknown_starttag(self, tag, attributes):
        self.handle_tag(tag, STARTTAG, attributes)
        htmllib.HTMLParser.unknown_starttag(self, tag, attributes)

    def unknown_endtag(self, tag):
        self.handle_tag(tag, ENDTAG, [])
        htmllib.HTMLParser.unknown_endtag(self, tag)

    def handle_data(self, data):
        if truth(Search_NotSpace.search(data)):
            print >>FileLog, data
#            for c in data: print >>FileLog, ord(c),
#            print >>FileLog
        htmllib.HTMLParser.handle_data(self, data)

#print >>FileLog, '\n         Template Test...\n'

#FileTemplate = "lst_template.hpt"
#FileT=open(WorkPath + os.sep + FileTemplate, 'rb')

#TP=HTTemplateParser(formatter.NullFormatter())
#TP.feed(FileT.read())
#TP.close()
