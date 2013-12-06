#!/usr/bin/env python
#################################################
# Create a zeitcoin peer for testing the network
#################################################

import sys, os, threading, subprocess
from zeitcoindb import hashtable
from zeitcoinutility import utility,encyption,logfile
from zeitcoinjsonrpc import zeitjsonrpc
from zeitcointrans import transactions
from zeitcoinforth import zeitforth
from zeitcoinamp import *

# Global Variables and constants
TGflag = 0        	  # This flag is set to 1 if it is designated as a tour guide
Leaderflag = 0   	  # This flag is set to 1 if it is designated as a leader
Tourflag = 0	  	  # This flag is set to 1 if this peer is in a tour
Leaderaddress = ''        # This will store the leader address
Leaderport = ''           # This will store the leader port
Leaderguid = ''           # This will store the leader guid
Clientaddress = ''        # This will store the client address
Clientport = ''           # This will store the client port
Clientguid = ''           # This will store the client guid
GTlist = ''               # Will hold the tour guides (guid,address,port)
ADDRESS='127.0.0.1'
FNAME='zeitcoin'
peerlist=[]
nodelist=[]
COMFLAG=0
ALIVE=1
PORT=1234

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "finish with the JSON-RPC command..."
    #reactor.stop()

def testjsonrpc(com1):
	proxy = Proxy('http://127.0.0.1:7080/')
	d = proxy.callRemote(com1)
	d.addCallback(printValue).addErrback(printError).addBoth(shutDown)
	#reactor.run()

def startservers(): 
	# Start the amp server
	global FNAME,ADDRESS,PORT
	lf=logfile()
	pf = Factory()
	zt=Zeit
	pf.protocol = zt
	reactor.listenTCP(PORT, pf)
	reactor.listenTCP(PORT+1000, server.Site(zeitjsonrpc()))
	lf.printinfo("servers started for "+str(ADDRESS)+" on port "+str(PORT)+"...")

def createdb():
	global FNAME
	ht=hashtable()
	conn,c=ht.connectdb(FNAME)
	ht.createht(conn,c)
	ht.createwallet(conn,c)
	ht.createtb(conn,c)
	ht.createlt(conn,c)
	ht.createaccount(conn,c)
	ht.createleader(conn,c)
	return

def createkeys():
	en=encyption()
	en.generatewalletkeys()
	return

def parameters():
	# checking for file and inital data and set the up if they don't exit
	# check for database file and if don't exist set up the hash table based on address,port given
	global FNAME,ADDRESS,PORT
	if (len(sys.argv)!=4):
		print "[Error] - This script needs three arguments"
	ADDRESS=str(sys.argv[1])
	PORT=int(sys.argv[2])
	FNAME=str(sys.argv[3])
	dbname="./test/"+FNAME+".db"
	pubname="./test/"+FNAME+"-public.pem"
	if (os.path.isfile(dbname)==False):
		print "Creating the database"
		#createdb()
	if (os.path.isfile(pubname)==False):
		print "Creating the public and private keys"
		#createkeys()
	return

def main():
	parameters()
	startservers()
	reactor.run()
	
if __name__ == '__main__':
    main()
