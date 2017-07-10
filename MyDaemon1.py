#!/usr/bin/env python2.7  
  
import sys, time  
from daemon1 import Daemon  
from Huangzblog1 import mylog
import threading
from Agent2 import *
import pyMongo,pymongo
from HuangzbSocketdoor import*
import xpath

class MyDaemon(Daemon):  
    def run(self):
        socketmain(self.Fparamfilename, self.flog)
  
if __name__ == "__main__":  
    f = open('test.log', "w")
    mylog(1,f,"DEBUG: log is build" )
    strusername = getpass.getuser()
    Gparamfilename = sys.argv[0]
    # print "Gparamfilename="+Gparamfilename
    Gparamfilename = Gparamfilename.replace(".py", ".xml")
    print("Gparamfilename=" + Gparamfilename)

    try:
        myxmldoc = xml.dom.minidom.parse(Gparamfilename)  # 读取整个文件的内容到内存,然后关掉文件
        for node in xpath.find("//xmlini/section[@name = $sname]/key[@name = $kname]", myxmldoc, sname="server",
                               kname="userfileprefix"):
            # print (node, node.tagName, node.getAttribute("value"))
            strprefix = node.getAttribute("value")
            # print "strprefix=",strprefix
            break

        for node in xpath.find("//xmlini/section[@name = $sname]/key[@name = $kname]", myxmldoc, sname="server",
                               kname="agentport"):
            # print (node, node.tagName, node.getAttribute("value"))
            agentport = node.getAttribute("value")
            print
            "agentport=", agentport
    except:
        info = sys.exc_info()
        print("%s...ERROR...info[0]=%s.....info[1]=%s." % (Gparamfilename, info[0], info[1]))
        sys.exit(1)

    HuangzbSocketdoor.port = string.atoi(agentport)
    f = open(strprefix + strusername + ".log", "w")
    mylog(1, f, "PARAM:agentport=%s\n" % agentport)
    daemon = MyDaemon('/tmp/daemon-example.pid',Gparamfilename,f)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:  
            daemon.start()  
        elif 'stop' == sys.argv[1]:  
            daemon.stop()  
        elif 'restart' == sys.argv[1]:  
            daemon.restart()  
        else:
            print ("Unknown command")  
            sys.exit(2)  
        sys.exit(0)  
    else:  
        print ("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)  

