#coding=utf-8
#!/usr/bin/python

from HTMLParser import HTMLParser
import os
import re
import datetime
import time
from bs4 import BeautifulSoup



INDEX_ALL = "indexAll.html"
TEMPLATE_FILE = "template.prefix"

# fun Defines
def printHello():
    print("你好哈哈")
    return

# 0 遍历所有文件，找到index.html，并返回该文件的path
def fetchAllIndexHTML(rootDir, targetList):

    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        if os.path.isdir(path):
            fetchAllIndexHTML(path, targetList)
        elif os.path.basename(path) == "index.html":
            targetList.append(path)
    return


def editDetailHtmlLinkRelations(rootDir):
    list_dirs = os.walk(rootDir)
    oldStr = "document.location.href='../index.html'"
    newStr = "document.location.href='../../" + INDEX_ALL + "'"
    for root, dirs, files in list_dirs:
        # for d in dirs:
        #     print os.path.join(root, d)
        for f in files:
            fPath = os.path.join(root, f)
            if fPath.endswith('html'):
                targetF = open(fPath, "r+w")
                contentStr = "".join(targetF.readlines())
                if contentStr.find(oldStr) > 0:
                    contentStr = contentStr.replace(oldStr, newStr)
                    targetF.seek(0, 0)
                    targetF.write(contentStr)

                targetF.close()
    return


# 1 找到文件中的<tr>标签，其内部为战报的索引，返回类型为bs4.element.Tag的list
def findTrTag(fName):
    tags = []
    with open(fName, "r") as myfile:
        data = myfile.read().replace('\n', '')

    sp = BeautifulSoup(data)
    trList = sp.find_all('tr')
    for tr_i in trList:
        if (tr_i['class'])[0].startswith('row'):
            tags.append(tr_i)

    return tags



# 2 对找到的<tr>进行修改，在onclick的属性上添加index.html的父目录前缀，打通超链接
def addParentDirPath2OnclickAttri(tag, indexPath):
    dirName = os.path.basename(os.path.dirname(indexPath))+'/'
    onclickPartOne = "document.location.href='"
    for inputTag in tag.find_all('input'):
        inputTag['onclick'] = (inputTag['onclick'])[:len(onclickPartOne)]+dirName+(inputTag['onclick'])[len(onclickPartOne):]

    return

# 3 将添加父目录的tag，转换为string类型，并抹去所有</input>，因为原有生成的标签并没有包含</input>
def converTag2StringAndRemoveInputSuffix(tag):
    return (repr(tag)).replace('</input>', '')

# 4 将修改后的trStringList，基于模版文件生成新的html.
def writeToHtml(tagStrList):
    finalStr = "\n".join(tagStrList)
    with open(TEMPLATE_FILE, "r") as suffixFile:
        suffixBegin = suffixFile.read()
    suffixMiddle = "\n<h1><a href='../index.html'>返回</a></h1><br/>\n" + '<table class="content_table" border="1" width="100%">\n<tbody><tr class="header"><th align="center">日期</th><th>地城</th><th>&nbsp;</th></tr>'
    suffixEnd = "\n</tbody></table></body></html>"

    fileToWrite = open(INDEX_ALL, 'w')
    fileToWrite.write(suffixBegin + suffixMiddle+ finalStr + suffixEnd)
    fileToWrite.close()
    return

# 5 排序key方法
def tagStrsKeyForSort(tagStr):
    matchObj = re.search( r"[0-9]*年[0-9]*月[0-9]*日 [0-9]*:[0-9]*", tagStr, 0)
    if matchObj:
        resultStr = matchObj.group()
        resultDate = datetime.datetime.strptime(resultStr, '%Y年%m月%d日 %H:%M')
        return resultDate
    else:
        return 0.0
    return

# 主流程

## 修改相对链接
editDetailHtmlLinkRelations(".")

## 生成indexAll.html
indexNames = []
fetchAllIndexHTML(".", indexNames)
print "========================"
print indexNames
print "++++++++++++++++++++++++++"

tagStrs = []
for indexI in indexNames:
    if os.path.dirname(indexI) == '.':
        continue

    tagList = findTrTag(indexI)
    for tagI in tagList:
        addParentDirPath2OnclickAttri(tagI, indexI)
        tagStrI = converTag2StringAndRemoveInputSuffix(tagI)
        tagStrs.append(tagStrI)

tagStrs.sort(key=tagStrsKeyForSort, reverse=True)

writeToHtml(tagStrs)

print "done"


# wodP = WodParser()
# wodP.feed(data)








