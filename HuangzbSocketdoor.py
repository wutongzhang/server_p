#!/usr/bin/python
# -*- coding:utf-8 -*- 

import socket, traceback, os, sys, time,datetime
from threading import *
import binascii
import getpass
import string
import random
import Agent2
from Huangzblog1 import mylog

host = ''                               # Bind to all interfaces
port = 9999                             #default port
MAXTHREADS = 30
lockpool = Lock()
busylist = {}
waitinglist = {}
queue = []
sem = Semaphore(0)


def handleconnection(clientsock,f,myxmldoc):
    """Handle an incoming client connection."""
    lockpool.acquire()
    mylog(3,f,"DEBUG:Received new client connection.")
    try:
        if len(waitinglist) == 0 and (activeCount() - 1) >= MAXTHREADS:
            # Too many connections.  Just close it and exit.
            clientsock.close()
            return
        if len(waitinglist) == 0:
            startthread(f,myxmldoc)

        queue.append(clientsock)
        sem.release()
    finally:
        lockpool.release()

def startthread(f,myxmldoc):
    # Called by handleconnection when a new thread is needed.
    # Note: lockpool is already acquired when this function is called.
    mylog(3,f,"DEBUG:Starting new client processor thread.")
    t = Thread(target = threadworker,args=(f,myxmldoc))
    t.setDaemon(1)
    t.start()

def threadworker(f,myxmldoc):
    global waitinglist, lockpool, busylist
    mylog(3,f,"DEBUG:starting....threadworker.....")
    time.sleep(1) # Simulate expensive startup
    name = currentThread().getName()
    try:
        lockpool.acquire()
        try:
            waitinglist[name] = 1
        finally:
            lockpool.release()
        
        processclients(f,myxmldoc)
    finally:
        # Clean up if the thread is dying for some reason.
        # Can't lock here -- we may already hold the lock, but it's OK
        print("** WARNING** Thread %s died" % name)
        if name in waitinglist:
            del waitinglist[name]
        if name in busylist:
            del busylist[name]

        # Start a replacement thread.
        startthread()


def listener(f,myxmldoc):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    timeout = 2000
    socket.setdefaulttimeout(timeout)
    s.listen(1)

    while 1:
        try:
            clientsock, clientaddr = s.accept()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            continue

        handleconnection(clientsock,f,myxmldoc)

def socketmain(paramfilename,flog):
    strusername=getpass.getuser()
    #f = open("/tmp/huangzb-pyserver-"+strusername+".log", "w")
    #probe something about os,mpi,etc.
    mylog(1,flog,'\n\nSTART LISTENER......................\n\n')
    
    myxmldoc=xml.dom.minidom.parse(paramfilename) 
    
    listener(flog,myxmldoc)
    while 1:
        mylog(3,flog,'Idle.... %s\n' % time.ctime(time.time()))
        time.sleep(100)        

def processclients(f,myxmldoc):
    global sem, queue, waitinglist, busylist, lockpool
    name = currentThread().getName()
            
    while 1:
        sem.acquire()
        lockpool.acquire()
        try:
            clientsock = queue.pop(0)
            del waitinglist[name]
            busylist[name] = 1
        finally:
            lockpool.release()

        try:
            mylog(1,f,"\n\nSTART TO DEAL WITH THE Request from Clients........\n\n")
            mylog(3,f,"processclients;[%s] Got connection from %s \n" % (name, clientsock.getpeername()))
            data=clientsock.recv(2048)
            mylog(3,f,"\nprocessclients;data="+data+" data.find(ASKING)=%d\n"%data.find("ASKING"))
            
            if (data.find("ASKING")>=0):
                clientsock.sendall("GREETI")
                data=clientsock.recv(1024)
                mylog(3,f,"processclients;data=%s" % data)
                while ((len(data)>0) and (data.find("OVER")==-1)):
                   handle_req(clientsock,data)
            else:
                mylog(3,f,"\nprocessclients;data="+data+" len(data)=%d" % len(data))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            traceback.print_exc()
            info=sys.exc_info()
            mylog(1,f,"...ERROR...info[0]=%s.....info[1]=%s."%(info[0],info[1]))
            

        # Close the connection

        try:
            clientsock.close()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()

        lockpool.acquire()
        try:
            del busylist[name]
            waitinglist[name] = 1
        finally:
            lockpool.release()        

