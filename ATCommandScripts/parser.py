import os
import sys
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
from mobile_insight.analyzer import LogAnalyzer
from mobile_insight.monitor import OfflineReplayer

src = OfflineReplayer()
src.enable_log_all()
start_time = time.time()

if len(sys.argv) < 4:
    print "ERROR : Missing Arguments"
    print "Valid Call: python parser.py <filepathsrc> <filepathtar> <graphname>"
    print "e.g. python parser.py ./pckofinterest ./logs/20-Loop/mass/merge.mi2log 20-loop"
    exit()


#Log analyzer
class fileAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.log_analyzer = LogAnalyzer(self.OnReadComplete)

    def OnReadComplete(self):
        for x in range(0,len(self.log_analyzer.msg_logs)):
            print self.log_analyzer.msg_logs[x]
            print "==========================================================="
        print len(self.log_analyzer.msg_logs)
    def ReadFile(self):    
        self.log_analyzer.AnalyzeFile(filepath, pcktypes)

filepath = sys.argv[2]
graphname = sys.argv[3]
pcktypes = open(sys.argv[1],'r').readlines()
for i in range(0,len(pcktypes)):
    pcktypes[i] = pcktypes[i].replace('\n','')    
logreader = fileAnalyzer(filepath)
logreader.ReadFile()

print "File located and Read !"
pckout = open('./pcks-filtered.txt','w')
packetTally = []
# pckout = open("./pck-filtered",'w')
for x in range(0,len(pcktypes)):
    packetTally.append([pcktypes[x],0])
for j in range(0,len(logreader.log_analyzer.msg_logs)):
    for l in range(0,len(packetTally)):
        if logreader.log_analyzer.msg_logs[j]['TypeID'] == packetTally[l][0]:
            pckout.write(str(logreader.log_analyzer.msg_logs[j])+'\n')  
            packetTally[l][1]+=1    

# Prining Frequencies

for i in range(0,len(packetTally)):
    print packetTally[i]

timetaken = int(time.time() - start_time)
timetaken = datetime.timedelta(seconds=(timetaken))
print "Processing Time: " + str(timetaken)

# Plotting Frequencies    
x = []
y = []
for j in range(0,len(packetTally)):
    x.append(packetTally[j][0])
    y.append(packetTally[j][1])
    
packets = tuple(x)
frequency = tuple(y)
y_pos = np.arange(len(packets))        
plt.bar(y_pos,frequency,align='center',color='g')
plt.ylabel('Frequency')
plt.title('Log Packet Distribution (' + str(graphname)+')')
plt.xticks(y_pos,packets,fontsize=5)
plt.show()
