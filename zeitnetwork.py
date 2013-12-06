#!/usr/bin/env python
#########################################
# Create a zeitcoin network for testing
#########################################

import sys, os, threading, subprocess, shutil, sqlite3
from zeitcoindb import hashtable
from zeitcoinutility import utility,encyption,logfile
from zeitcoinjsonrpc import zeitjsonrpc
from zeitcointrans import transactions
from zeitcoinforth import zeitforth
from zeitcoinamp import *
from txjsonrpc.web import jsonrpc
from txjsonrpc.web.jsonrpc import Proxy

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

@defer.deferredGenerator
def showwallet(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Wallet table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetallwallet(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

@defer.deferredGenerator
def showhash(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Hash table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetallht(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

@defer.deferredGenerator
def showtb(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Block transaction table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetalltb(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

@defer.deferredGenerator
def showtl(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Local transaction table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetalltb(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

@defer.deferredGenerator
def showaccounts(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Accounts table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetallaccount(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

@defer.deferredGenerator
def showleader(port):
	global FNAME,PORT,peerlist
	if (port==PORT):
		db=FNAME
		address='127.0.0.1'
	else:
		for peer in peerlist:
			if (peer[1]==port):
				db="./test/"+str(peer[3])
				address=peer[0]
	print "=====Leader table for "+str(address)+":"+str(port)+"====="
	ht=hashtable()
	dbpool=ht.tconnectdb(db)
	wfd = defer.waitForDeferred(ht.tgetallleader(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	return

def printmenu():
	print "==========AMP Commands==========="
	print "0) Quit"
	print "1) Test ping command"
	print "2) Test getguid command"
	print "3) Test copyht command"
	print "4) Test getclosest command"
	print "5) Test sendpublickey command"
	print "6) Test join command"
	print "7) Test sendtotg command"
	print "8) Test boardcasttrans command"
	print "9) Test generatecoin command"
	print "10)Test getnumtb command"
	print "11)Test getleader command"
	print "12)Test setleader command"
	print "13)Test getpuzzle command"
	print "14)Test verifypuzzle command"
	print "15)Test acceptcoin command"
	print "16)Test updatetb command"
	print "17)Test leave command"
	print "18)Test leaderinfo command"
	print "19)Test initleader command"
	print "20)Test getnewaddress command"
	print "======JSONRPC Commands=========="
	print "30) Test getbalance command"
	print "31) Test newaddress command"
	print "32) Test getaccountbalance command"
	print "33) Test getaccount command"
	print "34) Test getaddress command"
	print "35) Test sendcoins command"
	print "36) Test gettransaction command"
	print "37) Test isintour command"
	print "38) Test istourguide command"
	print "39) Test isleader command"
	print "40) Test listtransaction command"
	print "41) Test listaccounttransaction command"
	print "42) Test listaddresstransaction command"
	print "43) Test backupwallet command"
	print "99) to see the menu"
	print "=======Database Commands=========="
	print "50) Show wallet table"
	print "51) Show hash table"
	print "52) Show transaction block table"
	print "53) Show transaction local table"
	print "54) Show accounts table"
	print "55) Show leader tabled"	

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "finish with the JSON-RPC command..."

def testjsonrpc(com1,address,port,arglist):
	jsonaddress="http://"+str(address)+":"+str(port)+"/"
	proxy = Proxy(jsonaddress)
	if (len(arglist)==0):
		d = proxy.callRemote(com1)
	elif (len(arglist)==1):
		d = proxy.callRemote(com1,arglist[0])
	elif (len(arglist)==2):
		d = proxy.callRemote(com1,arglist[0],arglist[1])
	elif (len(arglist)==3):
		d = proxy.callRemote(com1,arglist[0],arglist[1],arglist[2])
	else:
		print "[Error] - with the arguments for the jsonrpc command"
	d.addCallback(printValue).addErrback(printError).addBoth(shutDown)

def startservers(): 
        # Start the amp server
        global PORT
	lf=logfile()
        port1=raw_input("What port do you want the amp server to listen?\n")
        PORT=int(port1)
        port1=raw_input("What port do you want the jsonrpc server to listen?\n")
        jsonrpcport=int(port1)
	zt=Zeit
        pf = Factory()
        pf.protocol = zt
        reactor.listenTCP(PORT, pf)
        reactor.listenTCP(jsonrpcport, server.Site(zeitjsonrpc()))
        lf.printinfo("servers started for the testing peer ....")

@defer.deferredGenerator
def docommand(str1):
	global ALIVE
	arglist=[]
	cc=clientcommands()
    	zj=zeitjsonrpc()
    	ut=utility()
	ht=hashtable()
	randomguid=ut.generateguid()
	dbpool=ht.tconnectdb(FNAME)
	wfd = defer.waitForDeferred(ht.tgetguid(dbpool))
	yield wfd
	guid = str(wfd.getResult())
	ht.tclosedb(dbpool)
	comlist=str1.split(":")
	com1=str(comlist[0])
	address=str(comlist[1])
	port=int(comlist[2])
	if (int(com1)==32 or int(com1)==31 or int(com1)==34 or int(com1)==41):
		account=str(comlist[3])
	if (int(com1)==33 or int(com1)==42):
		transaddress=str(comlist[3])
	if (int(com1)==36):
		thash=str(comlist[3])
	if (int(com1)==40):
		startingtrans=int(comlist[3])
		numtrans=int(comlist[4])
	if (com1=="0"):
		ALIVE=0
		print "Quiting..."
		destroynetwork()
		reactor.stop()
	elif (com1=="1"):
		cc.doping(address,port,guid)
	elif (com1=="2"):
		cc.dogetguid(address,port)
	elif (com1=="3"):
		cc.docopyht(address,port)
	elif (com1=="4"):
		cc.dogetclosest(address,port,randomguid)
	elif (com1=="5"):
		cc.dosendpublickey(address,port)
	elif (com1=="6"):
		cc.dojoin(address,port)
	elif (com1=="7"): 
		cc.dosendtotg(address,port,'11111111111111111111111111',2,4,'2222',3333)
	elif (com1=="8"):
		cc.doboardcasttrans(address,port,'7','th966',111.12)
	elif (com1=="9"):
		cc.dogeneratecoin(address,port)
	elif (com1=="10"):
		cc.dogetnumtb(address,port)
	elif (com1=="11"):
		cc.dogetleader(address,port,guid)
	elif (com1=="12"):
		cc.dosetleader(address,port,guid)
	elif (com1=="13"):
		cc.dogetpuzzle(address,port,'1111','ho1111111',1111.22,5,'arr1arr2')
	elif (com1=="14"):
		cc.doverifypuzzle(address,port,'2222','h11111','h222222')
	elif (com1=="15"):
		cc.doacceptcoin(address,port,'2','3333',111.11)
	elif (com1=="16"):
		cc.doupdatetb(address,port,'4444')
	elif (com1=="17"):
		cc.doleave(address,port,guid)
	elif (com1=="18"): 
		cc.doleaderinfo(address,port,'2222','127.0.0.1',1234)
	elif (com1=="19"):
		cc.doinitleader(address,port)
	elif (com1=="20"):
		cc.dogetnewaddress(address,port)
	elif (com1=="30"):
		print "sending a getbalance JSON-RPC command"
		testjsonrpc('getbalance',address,port,arglist)
	elif (com1=="31"):
		print "sending a newaddress JSON-RPC command"
		arglist.append(account)
		testjsonrpc('newaddress',address,port,arglist)
	elif (com1=="32"):
		print "sending a getaccountbalance JSON-RPC command"
		arglist.append(account)
		testjsonrpc('getaccountbalance',address,port,arglist)
	elif (com1=="33"):
		print "sending a getaccount JSON-RPC command"
		arglist.append(transaddress)
		testjsonrpc('getaccount',address,port,arglist)
	elif (com1=="34"):
		print "sending a getaddress JSON-RPC command"
		arglist.append(account)
		testjsonrpc('getaddress',address,port,arglist)
	elif (com1=="35"):
		print "sending a sendcoins JSON-RPC command"
		testjsonrpc('sendcoins',address,port,arglist)
	elif (com1=="36"):
		print "sending a gettransaction JSON-RPC command"
		arglist.append(thash)
		testjsonrpc('gettransaction',address,port,arglist)
	elif (com1=="37"):
		print "sending a isintour JSON-RPC command"
		testjsonrpc('isintour',address,port,arglist)
	elif (com1=="38"):
		print "sending a istourguide JSON-RPC command"
		testjsonrpc('istourguide',address,port,arglist)
	elif (com1=="39"):
		print "sending a isleader JSON-RPC command"
		testjsonrpc('isleader',address,port,arglist)
	elif (com1=="40"):
		print "sending a listtransaction JSON-RPC command"
		arglist.append(startingtrans)
		arglist.append(numtrans)
		testjsonrpc('listtransaction',address,port,arglist)
	elif (com1=="41"):
		print "sending a listaccounttransaction JSON-RPC command"
		arglist.append(account)
		testjsonrpc('listaccounttransaction',address,port,arglist)
	elif (com1=="42"):
		print "sending a listaddresstransaction JSON-RPC command"
		arglist.append(transaddress)
		testjsonrpc('listaddresstransaction',address,port,arglist)
	elif (com1=="43"):
		print "sending a backwallet JSON-RPC command"
		testjsonrpc('backwallet',address,port,arglist)
	elif (com1=="99"):
		printmenu()
	elif (com1=="50"):
		showwallet(port)
	elif (com1=="51"):
		showhash(port)
	elif (com1=="52"):
		showtb(port)
	elif (com1=="53"):
		showtl(port)
	elif (com1=="54"):
		showaccounts(port)
	elif (com1=="55"):
		showleader(port)
	else:
		print "Did not recognized the command"
        return

def getinput():
        # Get input for menu
	global ALIVE
	if (ALIVE==1):
		com1=raw_input("What command do you want to test?\n")
		if (int(com1)>0 and int(com1)<99):
			address=raw_input("What is the address for this command?\n")
			flag1=False
			while (flag1==False):
				port=raw_input("What is the port for this command?\n")
				flag1=port.isdigit()
				if (flag1==False):
					print "The port has to be an integer"
			str1=str(com1)+":"+str(address)+":"+str(port)
			if (int(com1)==32 or int(com1)==31 or int(com1)==34 or int(com1)==41):
				account=raw_input("What is the account name?\n")
				str1+=":"+str(account)
			if (int(com1)==33 or int(com1)==42):
				address=raw_input("What is the address?\n")
				str1+=":"+str(address)
			if (int(com1)==36):
				thash=raw_input("What is the Transaction Hash (thsash)?\n")
				str1+=":"+str(thash)
			if (int(com1)==40):
				flag1=False
				while (flag1==False):
					startingtrans=raw_input("What is the starting transaction (integer)?\n")
					flag1=port.isdigit()
					if (flag1==False):
						print "The starting transaction has to be an integer"
				flag1=False
				while (flag1==False):
					numtrans=raw_input("How many transaction to be listed?\n")
					flag1=port.isdigit()
					if (flag1==False):
						print "The number of transactions has to be an integer"
				str1+=":"+str(startingtrans)+":"+str(numtrans)
		else:
			str1=str(com1)+":1:1"
	return str1

def runagain(d):
	runinput()
	return

def runinput():
	d = threads.deferToThread(getinput)
	d.addCallback(docommand)
	d.addCallback(runagain)
	return d

def destroynetwork():
	global nodelist
	print "Shutting down the Network....."
	for node in nodelist:
		node.terminate()
	print "Finish with the Network"
	return

def createnetwork(peerlist):
	print "Creating Network....."
	nodelist=[]
	for peer in peerlist:
		time1=time.time()
		filename=peer[3]
		guid1=peer[2]
		address=peer[0]
		port=peer[1]
		str1="python ./zeitnode.py "+str(address)+" "+str(port)+" "+str(filename)
		print "str1=",str1
		p1 = subprocess.Popen("python ./zeitpeer.py "+str(address)+" "+str(port)+" "+str(filename),shell=True, stdout=None,stderr=None)
		nodelist.append(p1)
	print "Network is running...."
	return nodelist

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
	ht.closedb(conn)
	return

def refreshingdb(htlist):
	global FNAME
	print "Refreshing the database"
	ht=hashtable()
	gt=guidedtour()
	ht=hashtable()
	time1=gt.gettimestamp()
	conn,c=ht.connectdb(FNAME)
	ht.deleteleader(conn,c)
	ht.deleteallht(conn,c)
	ht.deletealllocaltrans(conn,c)
	ht.deleteallblocktrans(conn,c)
	ht.deleteallaccounts(conn,c)
	#ht.deleteallwallet(conn,c)
	#ht.addwallet(conn,c,guid,0,time1)
	for item in htlist:
		time1=gt.gettimestamp()
		ht.addht(conn,c,item[2],item[0],item[1],0,time1)
	ht.closedb(conn)
	return

def createkeys1(file1):
	file1="./test/"+file1
	en=encyption()
	en.generatewalletkeys(file1)
	return

def createkeys():
	global FNAME
	en=encyption()
	en.generatewalletkeys(FNAME)
	return

def copydb(file1):
	file1= "./test/"+file1+".db"
	shutil.copy2('zeitcoin.db', file1)
	return

def initpeers(peerlist):
	balance=0
	for peer in peerlist:
		time1=time.time()
		file1=peer[3]
		guid1=peer[2]
		createkeys1(file1)
		copydb(file1)
		db="./test/"+str(file1)+".db"
		conn = sqlite3.connect(db)
		c = conn.cursor()
		c.execute("INSERT INTO wallet VALUES ('"+str(guid1)+"','"+str(balance)+"','"+str(time1)+"')")
		conn.commit()
		c.execute("DELETE from hashtable where guid='"+guid1+"'")
		conn.commit()
		conn.close()
	return

def createpeers(peernum,startingport):
	ut=utility()
	peerlist=[]
	for i in range(0,int(peernum)):
		list1=[]
		guid=ut.generateguid()
		address='127.0.0.1'
		port=int(startingport)+int(i)
		filename="test"+str(i)
		list1.append(address)
		list1.append(port)
		list1.append(guid)
		list1.append(filename)
		peerlist.append(list1)
	return peerlist

def parameters():
	# checking for file and inital data and set the up if they don't exit
	# check for database file and if don't exist set up the hash table based on address,port given
	global FNAME
	dbname=FNAME+".db"
	pubname=FNAME+"-public.pem"
	if (os.path.isfile(dbname)==False):
		print "Creating the database"
		createdb()
	if (os.path.isfile(pubname)==False):
		print "Creating the public and private keys"
		createkeys()
	return

def main():
	global nodelist,peerlist
	print "Testing platform for the zeitcoin network"
	parameters()
	startservers()
	res=raw_input("Do you want to run the demo network (y)es/(n)o?\n")
	if (res=="y" or res=="yes"):
		peernum=raw_input("How many peers will be in the network?\n")
		startingport=raw_input("What will be the starting port?\n")
		peerlist=createpeers(peernum,startingport)
		refreshingdb(peerlist)
		initpeers(peerlist)
		nodelist=createnetwork(peerlist)
	printmenu()
	runinput()
	reactor.run()
	sys.exit(0)
	
if __name__ == '__main__':
    main()
