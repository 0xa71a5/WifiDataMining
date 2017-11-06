#encoding=utf-8
#import pandas as pd
import sqlite3
import numpy as np
import pickle
from collections import Counter

print "Load bin file to memory..."
#logTumple = pickle.load(open("sqlresult.tumple.bin","rb"))  #反序列化工作日日志
locationsMap = pickle.load(open("locationsMap.map.bin","rb")) #反序列化所有地点字符映射
macTumple = pickle.load(open("macs.tumple.bin","rb")) #反序列化所有mac地址
#log = pd.DataFrame(logTumple) # 元组转DF
#log = logTumple
sql = sqlite3.connect("log.db")
cur =sql.cursor() 
log = cur.execute("select time,mac,location from log where time>=508000000 and time <513000000").fetchall()
log += cur.execute("select time,mac,location from log where time>=515000000 and time <520000000").fetchall()
log += cur.execute("select time,mac,location from log where time>=522000000 and time <527000000").fetchall()

#macRowName = [macTumple[index] for index in range(10)]
macRowName = macTumple
#macVec_ = np.zeros([10,40],dtype = "uint16") #先测试10个mac地址 每个mac地址对应 8*5 个时空向量
#macVec = pd.DataFrame(macVec_,index=macRowName) #行名称为mac地址

timeSlice = [(0,60000),(60000,93500),(93500,121500),(121500,140000),(140000,153500),(153500,181500),(181500,205500),(205500,235959)] # 时间刻度
daySliceT = [x for x in range(508,513)]+[x for x in range(515,520)]+[x for x in range(522,527)]
daySlice={}
for index,day in enumerate(daySliceT):
    daySlice[day]=index
# 5.08 - 5.12

print "Initiaze time map"
timeMap=[7]*480 #用来做时间映射
for index,x in enumerate(timeSlice):
    front = x[0]/500
    back = x[1]/500
    for y in range(front,back):
        timeMap[y] = index

macMatrix = {} #这是用来存储时空特征向量的矩阵
days = 5*3 #一共出现的天数 每周5天 一共3周
#macMatrix2 ={}
for macName in macRowName:#18486个mac地址
    macMatrix[macName] = []
    #macMatrix2[macName] = []
    for x in range(8*days): #每天8个时间段  所有的时间段 为  8*days
        macMatrix[macName].append(set()) #为了开辟完整的空间，所以每次都是append 不过耗时不大
        #macMatrix2[macName].append(139)

firstDay = 508 #标记起始日期
length = len(log)

print "Begin calculate..."

for index in range(length): #遍历整个日志
    dayTime=0
    timeIndex=0
    try:
        logtime,mac,location = log[index]
        locationIndex = locationsMap[location] #获得地点转换后的数值位置
        dayTime = logtime/1000000 #
        clockTime = (logtime-dayTime*1000000)/500 #每5分钟做一次时间切片
        #print log.loc[index]
        #print clockTime
        timeIndex = daySlice[dayTime]*8 + timeMap[clockTime]
        #print "mac:{} timeindex:{} locationIndex:{}".format(mac,timeIndex,locationIndex)
        macMatrix[mac][timeIndex].add(locationIndex)
        if(index%5000==0):print index,index*100/length
    except Exception as e:
        print e
        if(mac not in macMatrix):
            macMatrix[mac] = []
            #macMatrix2[macName] = []
            for x in range(8*days): #每天8个时间段  所有的时间段 为  8*days
                macMatrix[mac].append(set())
            index-=1

print "Write macMatrix.bin to file"
pickle.dump(macMatrix,open("macMatrix2.bin","wb"))

'''
print "Begin translate..."

keys = macMatrix.keys()
for mac in keys:
    for index,timeSegment in enumerate(macMatrix[mac]):
        if(len(timeSegment)!=0):
            mostLocationIndex = Counter(timeSegment).most_common(1)[0][0] #获取到每个时间段出现次数最多的地点
            macMatrix2[mac][index] = mostLocationIndex
'''

print "Done!"

'''
# 这一段代码的时间复杂度过大
for mac in macRowName:
    for index,dayPoint in enumerate(daySlice):
        for index2,timePoint in enumerate(timeSlice):
            frontPoint = dayPoint+timePoint[0]
            endPoint = dayPoint + timePoint[1]
            print frontPoint,endPoint
            r = log[(log[0]>=frontPoint) & (log[0]<endPoint) & (log[1].str.contains(mac))]
            if ( len(r) != 0 ):
                mostHitLocPlaceIndex = locationsMap[r[2].describe()[2]]
                macVec[mac,index*8+index2] = mostHitLocPlaceIndex
                print mac,index*8+index2,mostHitLocPlaceIndex
'''






