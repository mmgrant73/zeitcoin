#!/usr/bin/env python
#########################################
# Zeitcoin JSONRPC Class
#########################################

import sys
from zeitcoindb import hashtable
from zeitcoinutility import utility,encyption
from txjsonrpc.web import jsonrpc
from txjsonrpc.web.jsonrpc import Proxy
from twisted.internet import reactor, defer, threads
from twisted.web import server
from twisted.internet.threads import deferToThread 

ALIVE=1
FNAME='zeitcoin'
TGflag = 0        	  # This flag is set to 1 if it is designated as a tour guide
Leaderflag = 0   	  # This flag is set to 1 if it is designated as a leader
Tourflag = 0	  	  # This flag is set to 1 if this peer is in a tour

class zeitjsonrpc(jsonrpc.JSONRPC):
    
	def jsonrpc_getbalance(self):
		# Getbalance - get the current total balance
		global FNAME
		print "getbalance command was received"
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tgetguid)
		d.addCallback(ht.tgetbalance,dbpool)
		d.addCallback(self._getbalance,ht,dbpool)
		d.callback(dbpool)
		return d 

	def _getbalance(self,balance,ht,dbpool):
		print "got to _getbalance"
		ht.tclosedb(dbpool)
		return balance

	def jsonrpc_newaddress(self,account):
		# Newaddress - generates a new address
		global FNAME
		print "newaddress command was received"
		ut=utility()
		ht=hashtable()
		en=encyption()
		time1=ut.gettimestamp()
		address=ut.generateguid()
		pubkey,privkey=en.generatekeys()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.taddaccount,account,privkey,pubkey,address,time1)
		d.addCallback(self._getnewaddress,address,ht,dbpool)
		d.callback(dbpool)
		return d

	def _getnewaddress(self,dummy,address,ht,dbpool):
		print "got to _getnewaddress"
		ht.tclosedb(dbpool)
		return address

	def jsonrpc_getaccountbalance(self,account):
		# Getaccountbalance - get the balance for a particular account
		# have to think about this one needs fix
		global FNAME
		print "getaccountbalance command was received"
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tgetaccountbalance,account)
		d.addCallback(self._getaccountbalance,ht,dbpool)
		d.callback(dbpool)
		return d

	def _getaccountbalance(self,balance,ht,dbpool):
		print "got to _getaccountbalance"
		ht.tclosedb(dbpool)
		return balance

	def jsonrpc_getaccount(self,address1):
		# Getaccount - get the account name of an address
		global FNAME
		print "getaccount command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgetaccount,address1)
		d.addCallback(self._getaccount,ht,dbpool)
		d.callback(dbpool)
		return d

	def _getaccount(self,account,ht,dbpool):
		print "got to _getaccount"
		ht.tclosedb(dbpool)
		return account

	def jsonrpc_getaddress(self,account):
		# Getaddress - get a list of address of an account
		global FNAME
		print "getaddress command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgetaddresses,account)
		d.addCallback(self._getaddress,ht,dbpool)
		d.callback(dbpool)
		return	d

	def _getaddress(self,addresslist,ht,dbpool):
		print "got to _getaddress"
		ht.tclosedb(dbpool)
		return addresslist

	def jsonrpc_sendcoins(self):
		# Sendcoins - send coin to an address
		# have to look at this
		global FNAME
		print "sendcoins command was received"
		return

	def jsonrpc_gettransaction(self,thash):
		# Gettransaction - get data for a transaction given the transaction ID
		# have to look at this one
		global FNAME
		print "gettransaction command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgettb,thash)
		d.addCallback(self._gettransaction,ht,dbpool)
		d.callback(dbpool)
		return	d #txid,thash,ts

	def _gettransaction(self,txid,ht,dbpool):
		print "got to _gettransaction"
		ht.tclosedb(dbpool)
		return txid

	def jsonrpc_isintour(self):
		# Isintour - Tells rather the wallet is in a guided tour
		global Tourflag
		print "isintour command was received"
		return	Tourflag

	def jsonrpc_istourguide(self):
		# Istourguide - Tells rather the wallet is acting like a tour guide
		global TGflag
		print "istourguide command was received"
		return	TGflag

	def jsonrpc_isleader(self):
		# Isleader - Tells rather the wallet is currently a leader
		global Leaderflag
		print "isleader command was received"
		return Leaderflag

	def jsonrpc_listtransaction(self,start,length):
		# Listtransaction - list all transactions
		global FNAME
		print "listtransaction command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgetlisttrans,start,length)
		d.addCallback(self._listtransaction,ht,dbpool)
		d.callback(dbpool)
		return d
	
	def _listtransaction(self,translist,ht,dbpool):
		print "got to _listtransaction"
		ht.tclosedb(dbpool)
		return translist

	def jsonrpc_listaccounttransaction(self,account):
		# Listacounttransaction - list transaction for an account
		# have to look at this one
		global FNAME
		print "listaccounttransaction command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgetlistaccounttrans,account)
		d.addCallback(self._listaccounttransaction,ht,dbpool)
		d.callback(dbpool)
		return d

	def _listaccounttransaction(self,translist,ht,dbpool):
		print "got to _listaccounttransaction"
		ht.tclosedb(dbpool)
		return translist

	def jsonrpc_listaddresstransaction(self,address):
		# Listaddresstransaction - list transaction for that address
		global FNAME
		print "listaddresstransaction command was received"
		ht=hashtable()
		d = defer.Deferred()
		d.addCallback(ht.tgetaddresstrans,address)
		d.addCallback(self._listaddresstransaction,ht,dbpool)
		d.callback(dbpool)
		return d	

	def _listaddresstransaction(self,trans,ht,dbpool):
		print "got to _listaddresstransaction"
		ht.tclosedb(dbpool)
		return trans

	def jsonrpc_backupwallet(self,backupname):
		# Backupwallet - backups the database for the wallet
		# have to check this one out
		global FNAME
		print "backupwallet command was received"
		ut=utility()
		ut.backupwallet(backupname)
		return true

def printmenu():
	print "======JSONRPC Commands=========="
	print "0) Quit"
	print "1) Test getbalance command"
	print "2) Test newaddress command"
	print "3) Test getaccountbalance command"
	print "4) Test getaccount command"
	print "5) Test getaddress command"
	print "6) Test sendcoins command"
	print "7) Test gettransaction command"
	print "8) Test isintour command"
	print "9) Test istourguide command"
	print "10) Test isleader command"
	print "11) Test listtransaction command"
	print "12) Test listaccounttransaction command"
	print "13) Test listaddresstransaction command"
	print "14) Test backupwallet command"
	print "99) to see the menu"
	return

def docommand(str1):
	global ALIVE
	arglist=[]
	comlist=str1.split(":")
	com1=str(comlist[0])
	address=str(comlist[1])
	port=int(comlist[2])
	if (int(com1)==3 or int(com1)==2 or int(com1)==5 or int(com1)==12):
		account=str(comlist[3])
	if (int(com1)==4 or int(com1)==13):
		transaddress=str(comlist[3])
	if (int(com1)==7):
		thash=str(comlist[3])
	if (int(com1)==11):
		startingtrans=int(comlist[3])
		numtrans=int(comlist[4])
	if (com1=="0"):
		ALIVE=0
		print "Quiting..."
		reactor.stop()
	elif (com1=="1"):
		print "sending a getbalance JSON-RPC command"
		#d = threads.deferToThread(testjsonrpc,'getbalance',address,port,arglist)
		testjsonrpc('getbalance',address,port,arglist)
	elif (com1=="2"):
		print "sending a newaddress JSON-RPC command"
		arglist.append(account)
		testjsonrpc('newaddress',address,port,arglist)
	elif (com1=="3"):
		print "sending a getaccountbalance JSON-RPC command"
		arglist.append(account)
		testjsonrpc('getaccountbalance',address,port,arglist)
	elif (com1=="4"):
		print "sending a getaccount JSON-RPC command"
		arglist.append(transaddress)
		testjsonrpc('getaccount',address,port,arglist)
	elif (com1=="5"):
		print "sending a getaddress JSON-RPC command"
		arglist.append(account)
		testjsonrpc('getaddress',address,port,arglist)
	elif (com1=="6"):
		print "sending a sendcoins JSON-RPC command"
		testjsonrpc('sendcoins',address,port,arglist)
	elif (com1=="7"):
		print "sending a gettransaction JSON-RPC command"
		arglist.append(thash)
		testjsonrpc('gettransaction',address,port,arglist)
	elif (com1=="8"):
		print "sending a isintour JSON-RPC command"
		testjsonrpc('isintour',address,port,arglist)
	elif (com1=="9"):
		print "sending a istourguide JSON-RPC command"
		testjsonrpc('istourguide',address,port,arglist)
	elif (com1=="10"):
		print "sending a isleader JSON-RPC command"
		testjsonrpc('isleader',address,port,arglist)
	elif (com1=="11"):
		print "sending a listtransaction JSON-RPC command"
		arglist.append(startingtrans)
		arglist.append(numtrans)
		testjsonrpc('listtransaction',address,port,arglist)
	elif (com1=="12"):
		print "sending a listaccounttransaction JSON-RPC command"
		arglist.append(account)
		testjsonrpc('listaccounttransaction',address,port,arglist)
	elif (com1=="13"):
		print "sending a listaddresstransaction JSON-RPC command"
		arglist.append(transaddress)
		testjsonrpc('listaddresstransaction',address,port,arglist)
	elif (com1=="14"):
		print "sending a backwallet JSON-RPC command"
		testjsonrpc('backwallet',address,port,arglist)
	elif (com1=="99"):
		printmenu()
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
			if (int(com1)==3 or int(com1)==2 or int(com1)==5 or int(com1)==12):
				account=raw_input("What is the account name?\n")
				str1+=":"+str(account)
			if (int(com1)==4 or int(com1)==13):
				address=raw_input("What is the address?\n")
				str1+=":"+str(address)
			if (int(com1)==7):
				thash=raw_input("What is the Transaction Hash (thsash)?\n")
				str1+=":"+str(thash)
			if (int(com1)==11):
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
        # Start the jsonrpc server
        port1=raw_input("What port do you want the jsonrpc server to listen?\n")
        jsonrpcport=int(port1)
        reactor.listenTCP(jsonrpcport, server.Site(zeitjsonrpc()))
        print "JSON-RPC servers started ...."
	return

def main():
	print "Testing the zeitcoin jsonrpc classes...."
	startservers()
	printmenu()
	runinput()
	reactor.run()
	sys.exit(0)
	print "Finish testing the zeitcoin jsonrpc classes"
	sys.exit(0)
	 
if __name__ == "__main__" : main()
