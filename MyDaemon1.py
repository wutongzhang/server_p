#!/usr/bin/env python2.7  
  
import sys, time  
from daemon1 import Daemon  
from Huangzblog1 import mylog
from Agent2 import *


class MyDaemon(Daemon):
    def run(self):
        f = open('/tmp/test2.log', "w")
        my_socket(f)

if __name__ == "__main__":
    f = open('/tmp/test.log', "w")
    mylog(1,f,"DEBUG: log is build" )
    daemon = MyDaemon('/tmp/daemon-example.pid',f)
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

