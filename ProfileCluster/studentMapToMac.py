#encoding=utf-8
#import pandas as pd
import numpy as np
import pickle
from collections import Counter
import collections

print "Load bin file to memory..."
logTumple = pickle.load(open("sqlresult.tumple.bin","rb"))  #反序列化工作日日志
locationsMap = pickle.load(open("locationsMap.map.bin","rb")) #反序列化所有地点字符映射
macTumple = pickle.load(open("macs.tumple.bin","rb")) #反序列化所有mac地址
#log = pd.DataFrame(logTumple) # 元组转DF ##多此一举。。。


#macRowName = [macTumple[index] for index in range(10)]
macRowName = macTumple
#macVec_ = np.zeros([10,40],dtype = "uint16") #先测试10个mac地址 每个mac地址对应 8*5 个时空向量
#macVec = pd.DataFrame(macVec_,index=macRowName) #行名称为mac地址

timeSlice = [(0,60000),(60000,93500),(93500,121500),(121500,140000),(140000,153500),(153500,181500),(181500,205500),(205500,235959)] # 时间刻度
daySlice = [508000000,509000000,510000000,511000000,512000000] # 5.08 - 5.12

print "Initiaze time map"
timeMap=[7]*480 #用来做时间映射
for index,x in enumerate(timeSlice):
    front = x[0]/500
    back = x[1]/500
    for y in range(front,back):
        timeMap[y] = index

macMatrix = {} #这是用来存储时空特征向量的矩阵
#macMatrix2 ={}
for macName in macRowName:#18486个mac地址
    macMatrix[macName] = []
    #macMatrix2[macName] = []
    for x in range(40):
        macMatrix[macName].append([]) #为了开辟完整的空间，所以每次都是append 不过耗时不大
        #macMatrix2[macName].append(139)

firstDay =daySlice[0] / 1000000 #标记起始日期
length = len(log)

print "Begin calculate..."

for index in range(length): #遍历整个日志
    logtime,mac,location = log.loc[index]
    locationIndex = locationsMap[location] #获得地点转换后的数值位置
    dayTime = logtime/1000000
    clockTime = (logtime-dayTime*1000000)/500 #每5分钟做一次时间切片
    #print log.loc[index]
    #print clockTime
    timeIndex = (dayTime-firstDay)*8 + timeMap[clockTime]
    #print "mac:{} timeindex:{} locationIndex:{}".format(mac,timeIndex,locationIndex)
    macMatrix[mac][timeIndex].append(locationIndex)
    if(index%1000==0):print index,index*100/length

pickle.dump(macMatrix,open("macMatrix.bin","wb"))

print "Done!"

