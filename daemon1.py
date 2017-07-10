#!/usr/bin/env python3.6
  
import sys, os, time, atexit  
from signal import SIGTERM   
  
import string
from Huangzblog1 import mylog
class Daemon:  
    """ 
    A generic daemon class. 
     
    Usage: subclass the Daemon class and override the run() method 
    """  
    def __init__(self, pidfile,logfile,stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):  
        self.stdin = stdin  
        self.stdout = stdout  
        self.stderr = stderr  
        self.pidfile = pidfile  
		#self.Fparamfilename = paramfilename
        self.flog = logfile
        mylog(1,self.flog,"DEBUG:CREATE BaseDaemon.....")
        mylog(1,self.flog,"DEBUG:PIDFile="+pidfile)
		#mylog(1,self.flog,"DEBUG:Param FileName="+paramfilename)
      
    def daemonize(self):  
        """ 
        do the UNIX double-fork magic, see Stevens' "Advanced  
        Programming in the UNIX Environment" for details (ISBN 0201563177) 
        """  
        try:   
            pid = os.fork()   
            mylog(1,self.flog,"DEBUG:CREATE the child process by os.fork()...PID=%d" % pid)
            if pid > 0:  
                # exit first parent  
                sys.exit(0)   
            mylog(1,self.flog,"DEBUG:EXIT first parent process.")
        except OSError as e:   
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))  
            mylog(1,self.flog,"DEBUG:fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)  
      
        mylog(1,self.flog,"DEBUG:Child Process......PID=%d" % pid)
        mylog(1,self.flog,'DEBUG:GETCWD()=%s\n'%os.getcwd())#返回当前工作目录
        mylog(1,self.flog,'DEBUG:PWD=%s\n'%os.environ['PWD'])#显示整个路径名？
        mylog(1,self.flog,'DEBUG:PATH=%s\n'%sys.argv[0])
        mylog(1,self.flog,'DEBUG:%s\n'%os.path.split(sys.argv[0])[0])
        mylog(1,self.flog,'DEBUG:%d\n'%os.getcwd().find(os.environ['PWD']))
		#if (os.getcwd().find(os.path.split(sys.argv[0])[0])<0):
		#	sys.stderr.write('Running Directory is not in the script Directory!!\n!!PLEASE CHECK!!\n\n')
		#self.Fparamfilename=os.getcwd()+"/"+self.Fparamfilename
        # decouple from parent environment  
        os.chdir("/")   
        os.setsid()   
        os.umask(0)   
      
        # do second fork  
        try:   
            pid = os.fork()   
            mylog(1,self.flog,"DEBUG:CREATE the child process by os.fork()...PID=%d" % pid)			
            if pid > 0:  
                # exit from second parent  
                sys.exit(0)   
            mylog(1,self.flog,"DEBUG:EXIT second parent process.")
        except OSError as e:   
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))  
            sys.exit(1)   
      
        # redirect standard file descriptors  
        sys.stdout.flush()  
        sys.stderr.flush()  
        si = open(self.stdin, 'r')  
        so = open(self.stdout, 'a+')  
        se = open(self.stderr, 'a+')  
        os.dup2(si.fileno(), sys.stdin.fileno())  
        os.dup2(so.fileno(), sys.stdout.fileno())  
        os.dup2(se.fileno(), sys.stderr.fileno())  
      
        # write pidfile  
        atexit.register(self.delpid)  
        pid = str(os.getpid())  
        open(self.pidfile,'w+').write("%s\n" % pid)  
      
    def delpid(self):  
        os.remove(self.pidfile)  
  
    def start(self):  
        """ 
        Start the daemon 
        """  
        # Check for a pidfile to see if the daemon already runs  
        print("DEBUG:Starting the daemon......")
        mylog(1,self.flog,"DEBUG:CHECK for a pidfile to see if the daemon already runs")
        try:  
            pf = open(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  
      
        if pid:  
            message = "DEBUG:pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)  
            mylog(1,self.flog,message % self.pidfile)
            sys.exit(1)  
          
        # Start the daemon  
        mylog(1,self.flog,"DEBUG:Start the daemon......self.daemonize()")
        self.daemonize()
        self.run()  
  
    def stop(self):  
        """ 
        Stop the daemon 
        """  
        # Get the pid from the pidfile  
        try:  
            pf = open(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  
      
        if not pid:  
            message = "pidfile %s does not exist. Daemon not running?\n"  
            sys.stderr.write(message % self.pidfile)  
            return # not an error in a restart  
  
        # Try killing the daemon process      
        try:
            while 1:  
                os.kill(pid, SIGTERM)  
                time.sleep(0.1)  
        except OSError as err:  
            err = str(err)  
            if err.find("No such process") > 0:  
                if os.path.exists(self.pidfile):  
                    os.remove(self.pidfile)  
            else:  
                print (str(err))  
                sys.exit(1)  
  
    def restart(self):  
        """ 
        Restart the daemon 
        """  
        self.stop()  
        self.start()  
  
    def run(self):  
        print("DEBUG:Running the daemon......")
        """ 
        You should override this method when you subclass Daemon. It will be called after the process has been 
        daemonized by start() or restart(). 
        """  
