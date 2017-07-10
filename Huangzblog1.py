import socket, traceback, os, sys, time,datetime
from threading import *
import struct


def	mylog(level,f,msgstr):
	f.write("[%s]....%s\n"%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),msgstr))
	f.flush()
