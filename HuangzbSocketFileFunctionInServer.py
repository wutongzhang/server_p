#!/usr/bin/python
# -*- coding:utf-8 -*- 

import socket, traceback, os, sys, time, datetime
import stat
from threading import *
import struct
from Huangzblog1 import mylog
import string
import random
import binascii

BUFSIZE = 1024


def SendServerFileToClient_Fd1fle(clientsock, f):
    fullfilename = ""
    filename = ""
    mylog(3, f, "\n\nSendServerFileToClient:START....")

    FILEINFO_SIZE = struct.calcsize('<128s32sI8s')
    fhead = clientsock.recv(FILEINFO_SIZE)####谁告诉的文件头？
    mylog(3, f, "SendServerFileToClient,receiving fhead.....")

    filename, temp1, filesize, temp2 = struct.unpack('<128s32sI8s', fhead)
    mylog(3, f, "SendServerFileToClient:Unpack filename=%s,filesize=%d..........." % (filename, filesize))

    fullfilename = filename.decode("utf-16")
    filename = filename.strip("\00")
    # print "FD1FLE,",filename
    if (os.path.isfile(filename)):####这判断又是干嘛的？？？
        try:
            fileStats = os.stat(filename)
        except:
            info = sys.exc_info()
            mylog(3, f, "SendServerFileToClient:...ERROR...info[0]=%s.....info[1]=%s..." % (info[0], info[1]))

        clientsock.sendall('OK')
        mylog(3, f, "SendServerFileToClient:send OK to client")

        fullfilename = filename
        filename = filename.encode("UTF-8")
        FILEINFO_SIZE = struct.calcsize('<128s32sI8s')
        fhead = struct.pack('<128s11I', filename, 0, 0, 0, 0, 0, 0, 0, 0, os.stat(fullfilename).st_size, 0, 0)
        clientsock.send(fhead)
        mylog(3, f, "SendServerFileToClient,sending fhead.....")

        fp = open(fullfilename, 'rb')
        while 1:
            filedata = fp.read(BUFSIZE)
            if not filedata: break
            clientsock.sendall(filedata)
        fp.close()
        mylog(3, f, 'SendServerFileToClient:Send all data over......OK')
        clientsock.sendall("OK")
        mylog(3, f, "SendServerFileToClient:send OK to client")
        mylog(3, f, "SendServerFileToClient:END.....\n\n")
        return fullfilename
    else:
        clientsock.sendall('ERROR')
        mylog(3, f, "SendServerFileToClient:send ERROR to client\n\n")
    pass


def ReceiveFileOfUploadedFileFromClient_Fu1fle(clientsock, f):
    mylog(3, f, "\n\nReceiveFileOfUploadedFileFromClient:START....")
    FBUFSIZE = 1024
    SBUFSIZE = 1024

    FILEINFO_SIZE = struct.calcsize('<128s32sI8s')
    fhead = clientsock.recv(FILEINFO_SIZE)
    mylog(3, f, "\n\nReceiveFileOfUploadedFileFromClient:recv fhead....")

    srvfilepath, temp1, filesize, temp2 = struct.unpack('<128s32sI8s', fhead)
    mylog(3, f, "ReceiveFileOfUploadedFileFromClient:unpack filesize..srvfilepath=%s...." % srvfilepath)
    srvfilepath = srvfilepath.strip("\00")
    if (os.path.isdir(srvfilepath)):
        clientsock.sendall('OK')
        FILEINFO_SIZE = struct.calcsize('<128s32sI8s')
        fhead = clientsock.recv(FILEINFO_SIZE)
        # mylog(3,f,"FU1FLE,receiving fhead.....")
        mylog(3, f, "ReceiveFileOfUploadedFileFromClient: recv fhead")

        filename, temp1, filesize, temp2 = struct.unpack('<128s32sI8s', fhead)
        mylog(3, f, "ReceiveFileOfUploadedFileFromClient:unpack...filename=%s" % filename)
        # filename = srvfilepath+string.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','L','m','n','o','p','q','r','s','t'], 8)).replace(" ","")+"_"+filename.strip('\00')
        filename = srvfilepath + filename.strip('\00')
        mylog(3, f, "ReceiveFileOfUploadedFileFromClient:full file path and name=%s" % filename)

        fp = open(filename, 'wb')
        restsize = filesize
        # mylog(3,f,"ReceiveFileOfUploadedFileFromClient:Upload File To Cluster...filesize=%d"%filesize)
        while 1:
            if restsize > SBUFSIZE:
                filedata = clientsock.recv(SBUFSIZE)
            else:
                filedata = clientsock.recv(restsize)
            if not filedata: break
            fp.write(filedata)
            restsize = restsize - len(filedata)
            if restsize == 0: break
        fp.flush()
        fp.close()
        mylog(3, f, 'ReceiveFileOfUploadedFileFromClient:all data over...OK\n\n')
        time.sleep(0.1)
        clientsock.sendall("OK")
        mylog(3, f, "ReceiveFileOfUploadedFileFromClient:send OK to client")
        mylog(3, f, 'ReceiveFileOfUploadedFileFromClient:END.\n\n')
        return filename
    else:
        clientsock.sendall('ERROR')
        mylog(3, f, "ReceiveFileOfUploadedFileFromClient:send ERROR to client\n\n")

    pass
