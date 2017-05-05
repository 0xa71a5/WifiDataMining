import os,socket,sys,time,string
import re
import commands
import sys
reload(sys)
sys.setdefaultencoding("utf8")
bufsize=1500
port=514
pattern=re.compile("(\w\w\w\w\.\w\w\w\w\.\w\w\w\w)")
locationPattern=re.compile(ur"\(([\u4e00-\u9fa5\w\-\/]+)\)")
eventTypeDic={}

stationLocationMap={}
geoContainer={}

colors={"black":30,"red":31,"green":32,"yellow":33,"blue":34,"pink":35,"blue":36,"white":37}
def getColorWord(color,content):
  if(color in colors):
    return '\033[1;{}m{}\033[0m'.format(colors[color],content)
  else:
    return str(content)

def parseLog(log,printInfo=True,writeInfo=False,writePath="./"):
  if(log.find("+08:00")!=-1):
    syslog=log.decode("GB2312","ignore")
    splitInfo=["",""]+[x for x in syslog.split(" ") if x!=""]
    if(len(splitInfo)<5 or splitInfo[3]!='172.22.192.10'):print "Not standard syslog format input!";return
    splitInfo=splitInfo[4:]
    splitInfo[0]=splitInfo[0][1:]
    splitInfo[2]=splitInfo[2][:-1]
    eventType=splitInfo[3][1:-1]
    eventTime=" ".join(splitInfo[0:3])
    eventContent=" ".join(splitInfo[4:])
    macAddr=pattern.findall(eventContent)
    if(len(macAddr)>0):macAddr=macAddr[0];macAddr="{}:{}:{}:{}:{}:{}".format(macAddr[0:2],macAddr[2:4],macAddr[5:7],macAddr[7:9],macAddr[10:12],macAddr[12:])
    else:macAddr=""
    ##match location
    print eventTime,macAddr,
    locations=locationPattern.findall(eventContent)
    if(eventType=="APMG-6-STA_ADD"):
      if(len(locations)==1):
        print "%-35s %-35s "%(getColorWord("red"," "),getColorWord("green",locations[0]))
      else:
        print "%-35s "%(getColorWord("yellow",eventContent))
    elif(eventType=="APMG-6-STA_DEL"):
      if(len(locations)==1):
        print "%-35s %-35s "%(getColorWord("red"," "),getColorWord("red",locations[0]))
      else:
        print "%-35s "%(getColorWord("yellow",eventContent))
    elif(eventType=="DOT1X-6-USER_ONLINE_FAIL"):
      print "%-35s "%(getColorWord("yellow","online fail"))
      pass
    elif(eventType=="STAMG-5-STA_RSSI"):
      print "%-35s "%(getColorWord("yellow","rssi too low"))
      pass
    elif(eventType=="APMG-6-STA_CHANGE"):
      if(len(locations)==2):
        print "%-35s %-35s "%(getColorWord("red",locations[0]),getColorWord("green",locations[1]))
      else:
        print "%-35s "%(getColorWord("yellow",eventContent))
    elif(eventType=="ROAMING-6-ROAM_EVENT"):
      if(len(locations)==2):
        print "%-35s %-35s "%(getColorWord("red",locations[0]),getColorWord("green",locations[1]))
      else:
        print "%-35s "%(getColorWord("yellow",eventContent))
    elif(eventType=="NFPP_ARP_GUARD-4-SCAN"):
      print "%-35s "%(getColorWord("yellow","arp scan"))
    elif(eventType=="NFPP_ARP_GUARD-4-DOS_DETECTED"):
      print "%-35s "%(getColorWord("yellow","arp attack"))
    elif(eventType=="APMG-6-STA_UPDT"):
      loc=eventContent.split(",")
      if(len(loc)==6):
        location=loc[2].split(" ")[-1]
        ipaddr=loc[4].split(" ")[-1]
        print "%-35s %-35s %-35s"%(getColorWord("red"," "),getColorWord("green",location),getColorWord("green",ipaddr))
      else:
        print eventContent
    else:
      print getColorWord("yellow",eventContent)
  else:
    print "Not standard syslog format input!"

def parseLogFromFile(mac,filePath="remoteLog.txt"):
  rawContent=commands.getoutput("cat {}|grep {}".format(filePath,mac))
  rawContent=rawContent.split("\n")
  for line in rawContent:
    parseLog(line)

if __name__ =="__main__":
  parseLogFromFile("e402.9b4d.94a0")

if __name__ =="__main__2":
  try:
    file=open("log.txt","a")
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0",port))
  except:
    print("error bind")
    file.close()
    sys.exit(1)

  print ("----------------syslog is start----------------\n")
  try:
    while 1:
      try:
        data,addr=sock.recvfrom(bufsize)
        syslog=str(data).decode("GB2312","ignore")
        splitInfo=[x for x in syslog.split(" ") if x!=""]
        if(len(splitInfo)<5 or splitInfo[3]!='172.22.192.10'):continue
        splitInfo=splitInfo[4:]
        splitInfo[0]=splitInfo[0][1:]
        splitInfo[2]=splitInfo[2][:-1]
        eventType=splitInfo[3][1:-1]
        eventTime=" ".join(splitInfo[0:3])
        eventContent=" ".join(splitInfo[4:])
        macAddr=pattern.findall(eventContent)
        if(len(macAddr)>0):macAddr=macAddr[0];macAddr="{}:{}:{}:{}:{}:{}".format(macAddr[0:2],macAddr[2:4],macAddr[5:7],macAddr[7:9],macAddr[10:12],macAddr[12:])
        else:macAddr=""
        ##match location
        print eventTime,macAddr,

        locations=locationPattern.findall(eventContent)
        if(eventType=="APMG-6-STA_ADD"):
          if(len(locations)==1):
            print "%-35s %-35s "%(getColorWord("red"," "),getColorWord("green",locations[0]))
          else:
            print "%-35s "%(getColorWord("yellow",eventContent))
        elif(eventType=="APMG-6-STA_DEL"):
          if(len(locations)==1):
            print "%-35s %-35s "%(getColorWord("red"," "),getColorWord("red",locations[0]))
          else:
            print "%-35s "%(getColorWord("yellow",eventContent))
        elif(eventType=="DOT1X-6-USER_ONLINE_FAIL"):
          print "%-35s "%(getColorWord("yellow","online fail"))
          pass
        elif(eventType=="STAMG-5-STA_RSSI"):
          print "%-35s "%(getColorWord("yellow","rssi too low"))
          pass
        elif(eventType=="APMG-6-STA_CHANGE"):
          if(len(locations)==2):
            print "%-35s %-35s "%(getColorWord("red",locations[0]),getColorWord("green",locations[1]))
          else:
            print "%-35s "%(getColorWord("yellow",eventContent))
        elif(eventType=="ROAMING-6-ROAM_EVENT"):
          if(len(locations)==2):
            print "%-35s %-35s "%(getColorWord("red",locations[0]),getColorWord("green",locations[1]))
          else:
            print "%-35s "%(getColorWord("yellow",eventContent))
        elif(eventType=="NFPP_ARP_GUARD-4-SCAN"):
          print "%-35s "%(getColorWord("yellow","arp scan"))
        elif(eventType=="NFPP_ARP_GUARD-4-DOS_DETECTED"):
          print "%-35s "%(getColorWord("yellow","arp attack"))
        elif(eventType=="APMG-6-STA_UPDT"):
          loc=eventContent.split(",")
          if(len(loc)==6):
            location=loc[2].split(" ")[-1]
            ipaddr=loc[4].split(" ")[-1]
            print "%-35s %-35s %-35s"%(getColorWord("red"," "),getColorWord("green",location),getColorWord("green",ipaddr))
          else:
            print eventContent
        else:
          print getColorWord("yellow",eventContent)
        
        toWrite="{};{};{};{}\n".format(eventTime,macAddr,eventType,eventContent.encode("utf8","ignore"))
        file.write(toWrite)
        file.flush()
      except socket.error:
        print "socket error"
  except KeyboardInterrupt:
    sock.close()
    file.close()
    '''
    typeFile=open("eventType.txt","w")
    for key in eventTypeDic:
      print key,eventTypeDic[key]
      typeFile.write(key+":"+eventTypeDic[key]+"\n")
    typeFile.close()
    '''
    print ("------------------syslogd stop-------------\n")
    print "good bye"
    sys.exit()