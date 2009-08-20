#!pyton
# -*- coding: cp1251 -*-
# Tested on Python Release 2.3 Win32

#import codecs, sys
#__, __, reader, __ = codecs.lookup("cp1251") 
#encoder, __, __, writer = codecs.lookup("cp1251") 
#oemout = writer(FileLog) 
#ansiin = reader(FileD) 

#oemout.write('Начали...\n')

#import htmllib, formatter
# from operator import truth

import logging

import string
import sys
import os
import urllib
from types import *
import re
#import sre
#flags=re.LOCALE | re.MULTILINE | re.UNICODE | re.VERBOSE | re.DOTALL | re.IGNORECASE | sre.DEBUG
flags=re.LOCALE | re.MULTILINE | re.UNICODE | re.VERBOSE | re.DOTALL | re.IGNORECASE

class ConvertationFail(Exception):pass

def TagNFormat(str):
    """ Easy HTML Pretty Formatter"""
    return re.sub('(?P<Tag><(br|p)>)((?P=Tag)|(?!\n)(?!<(/|)(br|p)>))', '\g<Tag>\n', str)
    # ('<br>(?!\n)', '<br>\n',str)

def ParsePage(Page):
    # Разбор страницы
    
    PostsList=[]  # пустой список постов
    
    print >>FileLog, 'Parsing Page : ' + FileName
    print 'Parsing Page : ' + FileName
    #1    Forum Header & Footer 
    PageStructure=re.compile('''
        .{0,7000}?<table[^>]*?>      #  Page Header
        .{0,300}?<tr[^>]*?>
        .{0,300}?<td[^>]*?>
        (.{0,300}?<a\ href="(?P<PrevRef>lst_[0-9]*\.htm)">.{0,300}?(Предыдущий).{0,10}?</a>|)
        .{0,300}?<td[^>]*?>
        .*?\d{1,2}\ \S{1,20}?\ \d{2,4}\ -\ \d{1,2}\ \S{1,10}?\ \d{2,4}.{0,300}?  # Date - Date
        .{0,300}?<td[^>]*?>
        (.{0,300}?<a\ href="(?P<NextRef>lst_[0-9]*\.htm)">.{0,300}?(Следующий).{0,300}?</a>|)
        .{0,300}?</table>
        .{0,3000}?добавить\ новое
    
        (?P<Posts>.*)      # Messages
    
        <table[^>]{0,300}?>      # Page Footer
        .{0,300}?<tr[^>]*?>
        .{0,300}?<td[^>]*?>
        (.{0,300}?<a\ href="(?P=PrevRef)">.{0,300}?(Предыдущий).{0,300}?</a>|)
        .{0,300}?<td[^>]*?>
        .{0,300}?\d{1,2}\ \S{1,20}?\ \d{2,4}\ -\ \d{1,2}\ \S{1,20}?\ \d{2,4}.{0,300}?  # Date - Date
        .{0,300}?<td[^>]*?>
        (.{0,300}?<a\ href="(?P=NextRef)">.*?(Следующий).{0,300}?</a>|)
        .{0,300}?</table>
                        ''', flags)
    PSmatch=PageStructure.match(Page)
    if PSmatch == None:
        ErrMsg = 'Parsing Page Header&Footer Failed :-(\n' +\
           'Convertation Aborted at : ' + FileName
        parserlog.critical(ErrMsg)
        raise ConvertationFail(ErrMsg)
    # print match1.groups()
    print >>FileLog, 'Forum Header & Footer parsed'
    print 'Forum Header & Footer parsed'
    PrevRef=PSmatch.groupdict('')['PrevRef']
    NextRef=PSmatch.groupdict('')['NextRef']
    print >>FileLog, 'Предидущий лист : ' + PSmatch.groupdict('')['PrevRef']
    print >>FileLog, 'Следующий лист  : ' + PSmatch.groupdict('')['NextRef']
    print >>FileLog
    
    PageBody=PSmatch.group('Posts')
    
    #
    #3 begin repeating part
    #
    
    PagePos=0
    
    #print PagePos
    #print PageBody[PagePos:PagePos+600]
    
    while True:
        PostData={}
        # Reply On
        re3=re.compile('''
            .{0,300}?<a\ name="(?P<MsgID>\d*?)">     # Author e
            .{0,50}?<table[^>]*>
            .{0,50}?<tr[^>]*?>
            .{0,50}?<td[^>]*?>
            .{0,30}?<font\ size=2[^>]*?>(?P<ReplyOn>.*?)</font>   # Отклик на
            .{0,300}?</table>
                            ''', flags)
        match3=re3.search(PageBody, PagePos)
        if match3==None:
            if len(PageBody) - PagePos > 300:
                ErrMsg = 'Large undetected Body part :-(\n' +\
                  'Convertation Aborted at : ' + FileName + ' Body Pos : '+ str(PagePos) +\
                  '\nMessages found : ' + str(len(PostsList))
                parserlog.critical(ErrMsg)
                parserlog.info('Tail next part :\n'+\
                               PageBody[PagePos:PagePos+1000])
                raise ConvertationFail(ErrMsg)
            print 'Body End.'
            print 'Tail : ', len(PageBody) - PagePos
            print 'Messages found : ', len(PostsList)
            break
#        print 'Forum Post Detected'
        PagePos=match3.end()
        PostData['MsgID']=match3.group('MsgID')
        PostData['SourceFile']=FileName
        PostData['ReplyOn']=match3.group('ReplyOn')
        print >>FileLog
        print >>FileLog, 'Сообщение № : ' + match3.group('MsgID')
#        print >>FileLog, 'Источник    : ' + PostData['SourceFile'] + '#' + PostData['MsgID']
        print >>FileLog, 'Отклик на   : ' + match3.group('ReplyOn')
        
        #4 - Main message table
        re3=re.compile('''
            .{0,50}?<table[^>]*?>
            .{0,50}?<tr[^>]*?>
            .{0,50}?<td[^>]*?>
            .{0,500}?<font[^>]*?>
            .{0,500}?&nbsp;<b>(?P<Author>[^<>]*?)</font>             # Author
            .{0,300}?<td[^>]*?>
            .{0,300}?<font[^>]*?>
            .{0,300}?(?P<Date>\d{1,2}\ \S*?\ \d{2,4}).{0,300}?</font>  # Date
            .{0,300}?<td[^>]*?>
            .{0,300}?<font[^>]*?>
            .{0,300}?(?P<Time>\d{1,2}:\d{2}).{0,300}?</font>         #  Time
            .{0,300}?<td[^>]*?>
            .{0,300}?<font[^>]*?>
            .{0,300}?Cообщение\ №\ (?P<MsgID>\d+).{0,300}?</font>    # MsgID
            .{0,300}?<td[^>]*?>  # Отклик Редакт.
            .{0,1000}?<tr[^>]*?>
            .{0,300}?<td[^>]*?>
            .{0,300}?<font[^>]*?>.{0,300}?Тема:.{0,300}?</font>
            .{0,300}?<td[^>]*?>
            .{0,300}?(&nbsp;|)(?P<Topic>[^<>]*?)                              # Topic
            \s*</table>
        
            .{0,300}?<table[^>]*?>
            .{0,50}?<tr[^>]*?>
            .{0,300}?Заголовок:
            .{0,300}?<td[^>]*?>&nbsp;(?P<PostName>.[^<>]*?)  # Subtopic
            \s*<tr[^>]*?>
            .{0,300}?<td[^>]*?>\s*(?P<PostBody>.*?)      # Body
            \s*</table>
        
            .{0,300}?<table[^>]*?>
            .{0,50}?<tr[^>]*?>
            .{0,50}?<td[^>]*?>
            .{0,50}?<a\ href="mailto:(?P<AuthorMail>[^<>]*?)"[^>]*?>.{0,300}?</a> # Author e
            .{0,300}?<a\ href="(?P<AuthorWWW>[^<>]*?)"[^>]*?>.{0,600}?</a>
        
            (?P<Replies>.*?)                       # Возможные Оклики
        
            .{0,500}?<tr[^>]*?>
            .{0,30}?</table>
                            ''', flags)
        
        match3=re3.match(PageBody, PagePos)
        if match3 == None:
            ErrMsg = '\n\nMain message table dont match. :-(\n' +\
               'Convertation Aborted at : ' + FileName + ' Body Pos : ' + str(PagePos) +\
               '\nMessages found : ' + str(len(PostsList))
            print >>FileLog, ErrMsg
            print >>FileLog, 'Tail next part :'
            print >>FileLog, PageBody[PagePos:PagePos+1000]
            print ErrMsg
            raise ConvertationFail(ErrMsg)
        PagePos=match3.end()
#        print 'Forum Post parsed'
        print >>FileLog, 'Автор       : ' + match3.group('Author')
        print >>FileLog, 'Дата        : ' + match3.group('Date') + '  ' + match3.group('Time')
#        print >>FileLog, 'Сообщение № : ' + match3.group('MsgID')
        print >>FileLog, 'Тема        : ' + match3.group('Topic')
        print >>FileLog
        print >>FileLog, 'Топик       : ' + match3.group('PostName')
        print >>FileLog
        print >>FileLog, TagNFormat(match3.group('PostBody'))
        print >>FileLog
        print >>FileLog, 'Mailto      : ' + match3.group('AuthorMail')
        print >>FileLog, 'http://     : ' + match3.group('AuthorWWW')
        print >>FileLog, 'Отклики     : ' + match3.group('Replies')
    
        # MsgID must be compared with previous detection
        if not(string.find(match3.group('Topic'), 'Опусы и пародии, навеянные фант. произведениями') < 0):
            for Atr in ('Author', 'Date', 'Time', 'MsgID', 'PostName',\
                        'PostBody', 'AuthorMail', 'AuthorWWW', 'Replies'):
                PostData[Atr]=match3.group(Atr)
            print >>FileLog, 'Forum Post parsed'
            PostsList=[PostData] + PostsList
        else:
            ErrMsg = 'Wrong Topic. Post Skipped!'
            parserlog.warning(ErrMsg)
            parserlog.debug('Тема пропущенного сообщения : ' + match3.group('Topic'))
            print ErrMsg
    return {'PrevRef':PrevRef, 'NextRef':NextRef, 'PostsList':PostsList}
# end def ParsePage


def OutputPage(ParseResult):
    OutPageHeader = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>Новые хроники Каэр Морхена %s</title>
<meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
</head>

<body>
<center><h3>Новые хроники Каэр Морхена<br>
(<a href="%s" title="Оригинал в Форуме"><font size="-1">%s</font></a>)</h3>
<p><a href="%s">&lt;&lt;- Предыдущий лист</a> |
 <a href="%s">Следующий лист -&gt;&gt;</a></p>
</center>
'''
    
    OutPageBody = '''
<h4>%s<br>
<font size="-2">(<a href="%s" title="Оригинал сообщения в Форуме">№ %s</a>)</font></h3>
<p><font size="-1"><a href="The_Omniscient_third_person.htm" title="Информация об Авторе">%s</a> | От %s</font>
<p>
%s
<p>&nbsp;<p>
'''
    
    OutPageFooter = '''<center>(<a href="%s" title="Оригинал в Форуме><font size="-1">%s</font></a>)</p>
<p><a href="%s">&lt;&lt;- Предыдущий лист</a> | <a href="%s">Следующий лист -&gt;&gt;</a></p></center>
</body>
</html>
'''
    
    rePageRef = re.compile('.*?lst_(\d*)\.htm', flags)
    if ParseResult['PrevRef'] == '':
        PrevRefID = ''
    else:
        PrevRefID = rePageRef.match(ParseResult['PrevRef']).group(1)
        
    if ParseResult['NextRef'] == '':
        NextRefID = ''
    else:
        NextRefID = rePageRef.match(ParseResult['NextRef']).group(1)
    
    PostsList=ParseResult['PostsList']
    
    FileOut=open(OutPath + os.sep + 'opusi_' + PageID + '.htm', 'wb')
    # Header
    # Непонятно откуда взялись пустые страницы. XXX maybe remove empty pages...
    if len(PostsList)>0:
        Dates=PostsList[0]['Date'] + ' - ' + PostsList[-1]['Date']
    else:
        Dates='-- --- -- - -- --- --'
    FileOut.write(OutPageHeader % (Dates,\
                                   FileName, Dates,\
                                   'opusi_' + PrevRefID + '.htm', 'opusi_' + NextRefID + '.htm')\
                 )
    # Body`s
    for Post in PostsList:
        FileOut.write(OutPageBody % (Post['PostName'], 
                                     FileName + '#' + Post['MsgID'], Post['MsgID'],\
                                     Post['Author'], Post['Date'] + ' ' + Post['Time'],\
                                     TagNFormat(Post['PostBody']))\
                     )
    # Footer
    FileOut.write(OutPageFooter % (FileName, Dates,\
                                   'opusi_' + PrevRefID + '.htm', 'opusi_' + NextRefID + '.htm')\
                 )
    
    FileOut.close
# end def OutputPage

WorkPath = "E:\MMV\pt"
SourceCachePath = WorkPath + os.sep + "Cache"
OutPath = WorkPath + os.sep + "Out"
#FileName = "http://www.fiction.kiev.ua/forum/lst/lst_1577.htm"
FileName = "http://www.fiction.kiev.ua/forum/lst/lst_2277.htm"
#FileName = urllib.pathname2url("E:\MMV\pt\lst_3372.htm")
LogName = "Log.txt"
refresh = False
ManualStep = False

FileLog=open(WorkPath + os.sep + LogName, 'wb')

log = logging.getLogger('forum_parser')
parserlog = logging.getLogger('forum_parser.parser')

hdlrFile = logging.StreamHandler(FileLog)
formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')
hdlrFile.setFormatter(formatter)
log.addHandler(hdlrFile)

#hdlrBuffFile = logging.MemoryHandler(128 , logging.WARNING, hdlrFile) 
#hdlrBuffFile.setFormatter(formatter)
#log.addHandler(hdlrBuffFile)

hdlrCons = logging.StreamHandler()
hdlrCons.setFormatter(formatter)
log.addHandler(hdlrCons)

log.setLevel(logging.DEBUG)

log.info('Begin.')

KeyInt=False
while True:
    log.info('Page     : ' + FileName)
    fBase, fName = os.path.split(FileName)
    rePageID = re.compile('lst_(\d*)\.htm', flags)
    PageID = rePageID.match(fName).group(1)
    
    # Cached URL access
    if not(os.path.exists(SourceCachePath + os.sep + fName)) or refresh:
        # Download page
        try:
            log.info('Retriev url : ' + FileName)
            urllib.urlretrieve(FileName, SourceCachePath + os.sep + fName)
            log.info('Retriev complete.')
        except KeyboardInterrupt:
            #os.remove(SourceCachePath + os.sep + fName)
            #raise
            KeyInt=True
            pass
        if KeyInt: raise
    else:
        log.info('Use Cached.')
    FileD=open(SourceCachePath + os.sep + fName, 'rb')
    Page=FileD.read()
    
    ParseResult=ParsePage(Page)
    
    #print PagePos
    #print PageBody[PagePos:PagePos+400]
    
    print '   ## Page Parse Complete! ##'
#    print 'PrevRef: ', ParseResult['PrevRef']
    print 'NextRef: ', ParseResult['NextRef']
    
    # Output html Template
    try:
        print 'Output Formatted Page....'
        OutputPage(ParseResult)
        print 'Output Formatted Page Complete.'
    except KeyboardInterrupt:
        #os.remove(SourceCachePath + os.sep + fName)
        #raise
        KeyInt=True
        pass
    if KeyInt: raise
    
    if ParseResult['NextRef']=='':
        print 'No NextRef. End.'
        break
    else:
        FileName = fBase + '/' + ParseResult['NextRef']
    if ManualStep:
        raw_input('Press Enter for next page process...')
