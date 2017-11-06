#encoding=utf-8
import sqlite3
import collections
import pickle
import os

def zero():return 0
def timeContain(front,back):
    #过滤包含12,13,14周
    targetFront=12
    targetBack =14
    return front<=targetFront and back>=targetBack

sql = sqlite3.connect("studentclass.db")
cur = sql.cursor()
locationsMap = pickle.load(open("locationsMap.map.bin","rb")) 
macMatrix = pickle.load(open("macMatrix2.bin","rb"))

studentno =cur.execute("select studentno from studentclass group by studentno").fetchall()
classId = set()
for item in studentno:
    if(item[0]!=None):
        classId.add(item[0][:6])#获取班级编号


#将班级的课程时间进行数值化处理
classTimeTable={}
if("classTimeTable.dict.bin" not in os.listdir(".")): #如果还未生成过班级课程表 那么生成一次
    for classId_ in classId :
        #classId_ = "090142" # 测试
        print classId_
        classDic = collections.defaultdict(zero)
        classFetch = cur.execute("select studentno,startweek,endweek,weekday,startclass,\
            endclass,location from studentclass where studentno like '{}%'".format(classId_)).fetchall()

        for item in classFetch:
            classDic[item[1:]]+=1 #课程统计

        targetClassTime = []
        if(len(classDic)!=0): #首先必须可执行结果不为空
            sortResult = sorted(classDic.items(),key=lambda x:x[1],reverse = True)
            if(sortResult[0][1] > 5):# 重叠课程数量大于5，如果太小说明找不到合适的重叠课程
                #for index,item in enumerate(sortResult):
                #    print index,"\t",item
                maxHit = sortResult[0][1] #设定排序后最靠前的课程的重叠次数为最大值
                for item in sortResult:
                    if(item[1] == maxHit and timeContain(item[0][0],item[0][1])):#将时间限定在12-14周
                        targetClassTime.append( item[0] ) #将课程时间表加入到重叠列表中
        if(len(targetClassTime)!=0):
            classTimeTable[classId_]=targetClassTime
    pickle.dump(classTimeTable,open("classTimeTable.dict.bin","wb"))
else: #当前目录下已经包含了班级课程表 直接读取
    classTimeTable = pickle.load(open("classTimeTable.dict.bin","rb"))

keys = classTimeTable.keys()
#for x in range(100):
#    print len(classTimeTable[keys[x]])

#[(0,60000),(60000,93500),(93500,121500),(121500,140000),(140000,153500),(153500,181500),(181500,205500),(205500,235959)]
#           0 , 1 , 2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13, 14, 15
sub_time = [0 , 1 , 1 ,2 ,2 ,2 ,4 ,4 ,5 ,5 ,5  ,6  ,6  , 6 ]
error = 0 
if("parseTimeTable.dict.bin" not in os.listdir(".")):
    parseTimeTable = {}
    print "Begin parse"
    for key in classTimeTable:
        parseTimeTable[key]=[]
        for item in classTimeTable[key]:
            a = item[2]
            b = item[3]
            try:
                location = locationsMap[item[-1]]
            except:
                error+=1
                continue
            parseTimeTable[key].append( (0*5*8 + (a-1)*8 +sub_time[b],location,) ) #每周所表示的时刻映射成数字 一周五天 一天8个时间段 
            parseTimeTable[key].append( (1*5*8 + (a-1)*8 +sub_time[b],location,) ) #每周所表示的时刻映射成数字
            parseTimeTable[key].append( (2*5*8 + (a-1)*8 +sub_time[b],location,) ) #每周所表示的时刻映射成数字
    print "Begin dump"
    pickle.dump(parseTimeTable,open("parseTimeTable.dict.bin","wb"))
else:
    parseTimeTable = pickle.load(open("parseTimeTable.dict.bin","rb"))

def getClass(classId):#按照排名进行过滤
    testclass = parseTimeTable[classId]
    testresult = collections.defaultdict(zero)
    for mac in macMatrix:
        for classInfo in testclass:
            if(classInfo[1] in macMatrix[mac][classInfo[0]]):
                testresult[mac]+=1
    testresult = sorted(testresult.iteritems(),key=lambda x:x[1],reverse=True)
    return testresult[:30]

def getClass2(classId):#按照出现次数进行过滤
    testclass = parseTimeTable[classId]
    testresult = collections.defaultdict(zero)
    for mac in macMatrix:
        for classInfo in testclass:
            if(classInfo[1] in macMatrix[mac][classInfo[0]]):
                testresult[mac]+=1
    testresult = filter(lambda x:x[1]>=6,testresult.iteritems())
    testresult = sorted(testresult,key=lambda x:x[1],reverse=True)
    return testresult

mapResult = {}
error = 0

if("classMapResult.map.bin" not in os.listdir(".")):
    for classId_ in classId:
        try:
            result = getClass2(classId_)
        except:
            error+=1
            continue
        if(len(result)!=0):
            mapResult[classId_] = result
            for item in result:
                macMatrix.pop(item[0])
    print "Write"
    pickle.dump(mapResult,open("classMapResult.map.bin","wb"))
print "Done!"
