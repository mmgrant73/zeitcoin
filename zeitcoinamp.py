#!/usr/bin/env python
#########################################
# Zeitcoin AMP Class
#########################################

import sys, os, time, threading, hashlib, random
from zeitcoindb import hashtable
from zeitcoinutility import utility,encyption
from zeitcointrans import transactions
from twisted.protocols import amp
from twisted.protocols.amp import AMP
from twisted.web import server
from twisted.application import service, internet
from twisted.internet import reactor, defer, endpoints, task, threads
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Factory
from twisted.internet.threads import deferToThread 

ALIVE=1
FNAME='zeitcoin'
ADDRESS='127.0.0.1'
PORT=1234
GUID='1'
TXCOINHASH=''
TXADDRESS=''
TXMESSAGE=''

class Getuuid(amp.Command):
    	# Get a unique id for a peer (guid)
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Copyht(amp.Command):
    	# copy a peer hast table and give it to a newly joined peer
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Getnumtb(amp.Command):
	# Get the number of transaction in the transaction block
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.Integer())]

class Updatetb(amp.Command):
	# Tells the server to send the most recent txid
	arguments = [('thash', amp.String()),('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Encryptdata(amp.Command):
	# Tells the peer to encrypted the data send to it
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer()),('data', amp.String())]
	response = [('reply', amp.String())]

class Getnewaddress(amp.Command):
	# Tells the server to create a new account and send back its address
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer()),('account', amp.String())]
	response = [('reply', amp.String())]

class Getleader(amp.Command):
	# Tells the server to randomly select a leader by generating a guid and find the nearest peer
	arguments = [('clientaddress', amp.String()), ('clientport', amp.Integer()), ('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Setleader(amp.Command):
	# Tells the server to be the leader
	arguments = [('clientaddress', amp.String()), ('clientport', amp.Integer()), ('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.Boolean())]

class Sendtransaction(amp.Command):
	# Tells the server to be the leader
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer()), ('coinhash', amp.String()),('receiveraddress', amp.String()), ('message', amp.Integer())]
	response = [('reply', amp.Boolean())]

class Gettransaction(amp.Command):
	# Tells the server to be the leader
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.Boolean())]

class Boardcasttrans(amp.Command):
	# Tells the server to be the leader
	arguments = [('txid', amp.Integer()), ('thash', amp.String()), ('ts', amp.Float()),('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Generatecoin(amp.Command):
	# Tells the server to generate a new coin
	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Acceptcoin(amp.Command):
	# Tells the server to accept the newly generated coin
	arguments = [('txid', amp.Integer()), ('thash', amp.String()), ('ts', amp.Float()),('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Ping(amp.Command):
	# pings a given peer hash table to see what nodes are still alive and remove any that isn't from the hash table
	# should be ran once an hour or so
	#arguments = []
	arguments =[('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Donetourguide(amp.Command):
	# pings a given peer hash table to see what nodes are still alive and remove any that isn't from the hash table
	# should be ran once an hour or so
	#arguments = []
	arguments =[('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
	response = [('reply', amp.String())]

class Getpuzzle(amp.Command):
	# Tells the server to generate a new puzzle for a guided tour h0,ts,L,arraytg
    	arguments = [('guid', amp.String()),('h0', amp.String()),('ts', amp.Float()),('L', amp.Integer()),('arraytg', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Verifypuzzle(amp.Command):
	# Tells the server to verify a puzzle for a guided tour
    	arguments = [('guid', amp.String()),('h0', amp.String()),('hl', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.Boolean())]

class Leaderinfo(amp.Command):
	# Tells the server to be the leader
	arguments = [('address', amp.String()), ('port', amp.Integer()), ('guid', amp.String())]
	response = [('reply', amp.Boolean())]

class Initleader(amp.Command):
	# Tells the server to return the closest guid in it's hash table
    	arguments = [('message', amp.String()),('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Getclosest(amp.Command):
	# Tells the server to return the closest guid in it's hash table
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Getclosestpeer(amp.Command):
	# Tells the server to return the closest guid in it's hash table
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Sendpublickey(amp.Command):
	# Tells the server to send its public key 
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Join(amp.Command):
	# Tells the server that a new peer has join the network 
    	arguments = [('guid', amp.String()), ('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Leave(amp.Command):
	# Tells the server that a peer has left the network
    	arguments = [('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

class Sendtotg(amp.Command):
	# Tells the server that is acting like a tour guide to verify the hash sent to it from the client
    	arguments = [('hashvalue', amp.String()), ('stopnumber', amp.Integer()), ('length', amp.Integer()), ('guid', amp.String()), ('ts', amp.Float()),('guid', amp.String()),('address', amp.String()), ('port', amp.Integer())]
    	response = [('reply', amp.String())]

##########################################################################
# move to another file protocol which holds classes Ziet, clientcommands #
##########################################################################

class Zeit(amp.AMP):

	def getuuid(self,guid,address,port):
		# tested and works
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port) 
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a getuuid message ',d
		ut=utility(self.filename,self.address,self.port)
		guid=ut.generateguid()
		ut.updatepeer(guid,address,port)
		return {'reply': guid}
	Getuuid.responder(getuuid)

	def ping(self,guid,address,port):
		# tested and works
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a ping message ',d
		str1="hello: address - "+str(address)+" port - "+str(port)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': str1}
	Ping.responder(ping)

	def donetourguide(self,guid,address,port):
		# tested and works
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a donetourguide message ',d
		self.donewithtg(address,port)
		str1="ok"
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': str1}
	Donetourguide.responder(donetourguide)

	def getpuzzle(self,guid,h0,ts,L,arraytg,address,port): 
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a getpuzzle message ',d 
		gt=guidedtour()
		gt.getpuzzle(guid,h0,ts,L,arraytg)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Getpuzzle.responder(getpuzzle)

	def verifypuzzle(self,guid,h0,hl,address,port):
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a verifypuzzle message ',d
		result=True
		gt=guidedtour()
		#gt.verifyupuzzle(guid,h0,hl)
		flag=0
		keylist=[]
		h0=firsthash
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tnumtb)
		d.addCallback(ht.tgetkeys)
		d.addCallback(self._verifypuzzle,ht,dbpool)
		d.addCallback(ht.tdeleteleader,dbpool)
		d.addCallback(self.__verifypuzzle,ht,dbpool)
		d.callback(dbpool)
		#N=ht.numtg()
		#keyslist=ht.getkeys()
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return d #{'reply': result}
	Verifypuzzle.responder(verifypuzzle)

	def _verifypuzzle(self,ht,dbpool):
		print "got to _verifypuzzle"
		for i in range(0,L):
			tourindex=self.gettourindex(h0,N)
			key=keylist[tourindex]
			h0=self.tourguideverify(h0,i+1,L,clientguid,key,ts)
		#ht.deleteleader()
		if (h0==lasthash):
			result=True
			#store the transaction and boardcast it
		else:
			result=False
		print "message to verify h0-"+h0+" hl-"+hl+" from client-"+guid
		return result

	def __verifypuzzle(self,result,ht,dbpool):
		print "got to _verifypuzzle"
		ht.tclosedb(dbpool)
		return {'reply': result}

	def getnewaddress(self,guid,address,port,account):
		# Need to fix database (dbpool)
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a getnewaddress message ",d	
		ut=utility(self.filename,self.address,self.port)
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
		return d #{'reply': count1}
	Getnewaddress.responder(getnewaddress)

	def _getnewaddress(self,dummy,guid,address,ht,dbpool):
		print "got to _getnewaddress"
		print "newaddress - ",address 
		ht.tclosedb(dbpool)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': address}

	def getnumtb(self,guid,address,port):
		# Need to fix database (dbpool)
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a getnumtb message ",d
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tnumtb)
		d.addCallback(self._getnumtb,ht,dbpool)
		d.callback(dbpool)
		return d #{'reply': count1}
	Getnumtb.responder(getnumtb)

	def _getnumtb(self,count1,ht,dbpool):
		print "got to _getnumtb"
		ht.tclosedb(dbpool)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': count1}

	def updatetb(self,thash,guid,address,port):
		# Need to fix database (dbpool)
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a updatetb message ",d
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		#conn,c=ht.connectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tgetalltb)
		d.addCallback(self._updatetb,thash,ht,dbpool)
		d.callback(dbpool)
		#listtb=ht.getalltb(c)
		return d #{'reply': str(newtrans[1])}
	Updatetb.responder(updatetb)

	def _updatetb(self,listtb,thash,ht,dbpool):
		print "got to _updatetb"
		trans=listtb[0]
		thash1=trans[1]
		if (thash==thash1):
			newtrans=listtb[1]
		else:
			newtrans=list
		ht.tclosedb(dbpool)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': str(newtrans[1])}

	def getleader(self,clientaddress,clientport,guid,address,port):
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a getleader message ",d
		ut=utility(self.filename,self.address,self.port)
		result=self.getleader(address,port,guid)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Getleader.responder(getleader)

	def boardcasttrans(self,txid,thash,ts,guid,address,port):
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a boardcast messageb ",d
		ut=utility(self.filename,self.address,self.port)
		result=self.boardcasttrans(txid,thash,ts)
		return {'reply': 'ok'}
	Boardcasttrans.responder(boardcasttrans)

	def generatecoin(self,guid,address,port):
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a generatecoin message ",d
		#tx=transactions()
		self.generatenewcoin()
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Generatecoin.responder(generatecoin)

	def encryptdata(self,guid,address,port,data):
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received an encryptdata message ",d
		en=encyption()
		pubkey=en.getpubkey(FNAME)
		message=en.encyptmessage(data,pubkey)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': str(message)}
	Encryptdata.responder(encryptdata)

	def acceptcoin(self,txid,thash,ts,guid,address,port):
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received an acceptcoin message ",d
		tx=transactions()
		tx.acceptcoin(txid,thash,ts)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Acceptcoin.responder(acceptcoin)

	def setleader(self,clientaddress,clientport,guid,address,port):
		global Leaderflag,Clientaddress,Clientport,Clientguid,ADDRESS,PORT
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a setleader message ",d
		if (Leaderflag==1):
			result=False
		else:	
			# store client address,port and guid
			self.setleader(clientaddress,clientport,guid)	
			Leaderflag=1
			result=True
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': result}
	Setleader.responder(setleader)

	def sendtransaction(self,guid,address,port,coinhash,receiveraddress,message):
		global ADDRESS,PORT,FNAME,TXCOINHASH,TXADDRESS,TXMESSAGE
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a sendtransaction message ",d
		# store this information to be sent after guide tour
		TXCOINHASH=coinhash
		TXADDRESS=receiveraddress
		TXMESSAGE=message
		result=True
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': result}
	Sendtransaction.responder(sendtransaction)

	def gettransaction(self,guid,address,port):
		global ADDRESS,PORT,FNAME,TXCOINHASH,TXADDRESS,TXMESSAGE
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a sendtransaction message ",d
		# store this information to be sent after guide tour
		result=str(TXCOINHASH)+":"+str(TXADDRESS)+":"+str(TXMESSAGE)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': result}
	Gettransaction.responder(gettransaction)

	def leaderinfo(self,address,port,guid):
		global Leaderaddress, Leaderport, Leaderguid,ADDRESS,PORT
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		Leaderaddress=self.address
		Leaderport=self.port
		Leaderguid=guid
		print frm+" received a leaderinfo message ",d
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Leaderinfo.responder(leaderinfo)

	def initleader(self,message,guid,address,port):
		global self.filename,self.address,self.port
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a initleader message ",d
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': 'ok'}
	Initleader.responder(initleader)

	def sendpublickey(self,guid,address,port):
		# tested and works
		global self.filename,self.address,self.port
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		print frm+" received a sendpublickey message ",d
		en = encyption()
		pubkey=en.getpublickey(FNAME)
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': str(pubkey)}
	Sendpublickey.responder(sendpublickey)

	def join(self,guid,addres,port):
		# new peer join command
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		ut=utility(self.filename,self.address,self.port)
		guid=ut.generateguid()
		result=ut.getht()
		result+=guid
		return {'reply': result}
	Join.responder(join)

	def leave(self,guid,address,port):
		# peer leave command
		global ADDRESS,PORT,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+' received a leave message ',d
		self.leave(guid)
		return {'reply': 'ok'}
	Leave.responder(leave)

	def sendtotg(self,hashvalue,stopnumber,length,guid,ts,guid1,address,port):
	    	# h_{l} = hash(h_{l-1}\; ||\; l\; ||\; L\; ||\; A_{x}\; ||\; ts\; ||\; k_{js})
		# ks - pulled from public key
		# ts and guid will be stored by the tg and verify when sedtotg is called
		global ADDRESS,PORT,FNAME
		frm=str(self.address)+":"+str(self.port)
		d = str(self.address)+":"+str(self.port)
		gt=guidedtour()
		print frm+" received a sendtotg message ",d
		print "tour guided received h0-"+hashvalue+" stopnumber-"+str(stopnumber)+" L-"+str(length)+" guid-"+guid+" ts-"+str(ts)
		#result=gt.tourguideverify(hashvalue,stopnumber,length,guid,ts)
		result="true"
		ut=utility(self.filename,self.address,self.port)
		ut.updatepeer(guid,address,port)
		return {'reply': result}
	Sendtotg.responder(sendtotg)

	def copyht(self,guid,address,port):
		# tested and works
		global ADDRESS,PORT,FNAME,FNAME
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a copyht message ",d
		#ut=utility(self.filename,self.address,self.port)
		#result=ut.getht()
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tgetallht)
		d.addCallback(self._copyht,ht,dbpool)
		d.callback(dbpool)
		return d #{'reply': result}
	Copyht.responder(copyht)

	def _copyht(self,htlist,ht,dbpool):
		print "got to _copyht"
		result=''
		for row in htlist:
			result+=str(row[0])+","+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])+":"
		res=result[:-1]
		ht.tclosedb(dbpool)
		return {'reply': res}	

	def getclosest(self,guid,address,port):
		# Need to fix database (dbpool)
		global self.filename,self.address,self.port
		d = str(self.address)+":"+str(self.port)
		frm=str(self.address)+":"+str(self.port)
		print frm+" received a getclosest message ",d
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		d = defer.Deferred()
		d.addCallback(ht.tgetallguidht)
		d.addCallback(self._getclosest,guid,ht,dbpool)
		d.addCallback(ht.tgetaddress,dbpool)
		d.addCallback(self.__getclosest,ht,dbpool)
		d.callback(dbpool)
		return d #{'reply': result}
	Getclosest.responder(getclosest)

	def _getclosest(self,peerlist,guid,ht,dbpool):
		print "got to _getclosest"
		ut=utility(self.filename,self.address,self.port)
		guid1,d1=ut.closestpeer(guid, peerlist)
		print "dbpool ",dbpool
		print "guid1 ",guid1
		print "d1 ",d1
		#ht.tclosedb(dbpool)
		return guid1,d1

	def __getclosest(self,guid1,ht,dbpool):
		print "got to __getclosest"
		ht.tclosedb(dbpool)
		result=str(guid1)
		return {'reply': result}

	def getclosestpeer(self,guid):
		global CLOSESTGUID,CLOSESTADDRESS,CLOSESTPORT,CLOSESTDISTANCE
		d = defer.Deferred()
		d.addCallback(self._getclosestpeer)
		d.addCallback(self.__getclosestpeer)
		d.callback(guid)
		return d
	Getclosestpeer.responder(getclosestpeer)

	def __getclosestpeer(self,guid):
		global CLOSESTGUID,CLOSESTADDRESS,CLOSESTPORT,CLOSESTDISTANCE
		result= str(CLOSESTGUID)+":"+str(CLOSESTADDRESS)+":"+str(CLOSESTPORT)+":"+str(CLOSESTDISTANCE)
		return {'reply': result}

	@defer.deferredGenerator
	def _getclosestpeer(self,guid):
		global FNAME,CLOSESTGUID,CLOSESTADDRESS,CLOSESTPORT,CLOSESTDISTANCE
		flag=0
		d1=999999999999999999999999999999999999999999
		cc=clientcommands()
		ht=hashtable()
		ut=utility(self.filename,self.address,self.port)
		conn,c=ht.connectdb(FNAME)
		peerlist=ht.getallguidht(c)
		guid,d2=ut.closestpeer(peerid, peerlist)
		address,port=ht.getaddress(c,guid)
		ht.closedb(conn)
		if (d2==0): #[4^3 *3/(5-8)*(n^2+3)]^2+3*5+7=.19*(5+0.07)*5-2^2+5*2
			flag=1
			guid1=guid
		while (flag==0):
			#guid1,address,port,d2=cc.dogetclosest(address,port,guid) # use yield
			wfd = defer.waitForDeferred(cc.dogetclosest(address,port,guid))
    			yield wfd
			data = str(wfd.getResult())
			datalist=data.split(":")
			guid1=datalist[0]
			address=datalist[1]
			port=datalist[2]
			d2=datalist[3]
			if (d2==0):
				flag=1
			else:
				if (d2<d1):
					d1=d2
					address1=address
					port1=port
					guid2=guid1
				else:
					address=self.address1
					port=self.port1
					guid1=guid2
					flag=1
		CLOSESTaddress=self.address
		CLOSESTport=self.port
		CLOSESTGUID=guid1
		CLOSESTDISTANCE=D1
		#return guid1,address,port

	@defer.deferredGenerator
	def leave(self,guid):
		global FNAME
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tdeleteht(dbpool,guid))
		yield wfd
		ht.tclosedb(dbpool)
		print "Guid - "+guid+" is leaving the network"
		return

	def boardcasttrans(self,txid,thash,ts):
		global FNAME
		cc=clientcommands()
		ht=hashtable()
		ut=utility(self.filename,self.address,self.port)
		conn,c=ht.connectdb(FNAME)
		res=ht.checktrans(conn,c,txid)
		if (res==False):
			guid=ht.getguid(c)
			ht.addtb(conn,c,txid,thash,ts)
			peerlist=ht.getallguidht(c)
			guid1,d1=ut.closestpeer(guid,peerlist)
			guid2,d2=ut.farestpeer(guid,peerlist)
			address,port=ht.getaddress(c,guid1)
			address1,port1=ht.getaddress(c,guid2)
			print "closest peer ",guid1,address,port
			print "farest peer ",guid2,address1,port1
			cc.doboardcasttrans(address,port,txid,thash,ts)
			cc.doboardcasttrans(address1,port1,txid,thash,ts)
		else:
			print "already exist in the transaction block"
		return

	@defer.deferredGenerator
	def getleader(self,address,port,guid):
		global FNAME
		cc=clientcommands()
		ut=utility(self.filename,self.address,self.port)
		randomguid=ut.generateguid()
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		#conn,c=ht.connectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		peerlist = wfd.getResult()
		#peerlist=ht.getallguidht(c)
		guid1,d2=ut.closestpeer(randomguid, peerlist)
		wfd = defer.waitForDeferred(ht.tgetaddress(dbpool,guid1,d2))
		yield wfd
		data1 = wfd.getResult()
		address1=str(data1[0])
		port1=int(data1[1])
		#address1,port1=ht.getaddress(c,guid1)
		ht.tclosedb(dbpool)
		# check if the random is already a leader or a tour guide
		#res=self.setleader(address1,port)
		wfd = defer.waitForDeferred(cc.dosetleader(str(address1),int(port1),str(address),int(port),str(guid1)))
    		yield wfd
		res = wfd.getResult()
		print "res=",res
		wfd = defer.waitForDeferred(cc.doleaderinfo(str(address),int(port),str(guid1),str(address1),int(port1)))
    		yield wfd
		res = wfd.getResult()
		print "result-",res
		print "The leader will have guid - "+guid1+" address - "+address1+" port - "+str(port1)
		#wfd = defer.waitForDeferred(cc.doinitleader(str(address1),int(port1)))
    		#yield wfd
		#res = wfd.getResult()
		#print "result-",res
		return 

	@defer.deferredGenerator
	def setleader(self,address,port,guid):
		global Leaderflag,Clientaddress,Clientport,Clientguid,FNAME
		gt=guidedtour()
		Clientaddress=self.address
		Clientport=self.port
		Clientguid=guid
		#gtlist=gt.gettourguides()
		gtlist=[]
		N=random.randint(gt.MINTG,gt.MAXTG)
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		peerlist = wfd.getResult()
		wfd = defer.waitForDeferred(ht.tnumht(dbpool))
		yield wfd
		count1 = wfd.getResult()
		print "peerlist=",peerlist
		for i in range(1,N):
			gt = random.randint(0,count1-1)
			print "gt=",gt
			gtlist.append(peerlist[gt])
		gt.getsharedsecret(gtlist)
		return

	@defer.deferredGenerator
	def donewithtg(self,guid,address,port):
		global Leaderflag,Clientaddress,Clientport,Clientguid,FNAME,TXCOINHASH,TXADDRESS,TXMESSAGE, Leaderaddress,Leaderport
		wfd = defer.waitForDeferred(cc.dogettransaction(str(address),int(port)))
    		yield wfd
		res = str(wfd.getResult())
		listres=res.split(":")
		TXCOINHASH = str(listres[0])
		TXADDRESS = str(listres[1])
		TXMESSAGE = str(listres[2])
		wfd = defer.waitForDeferred(cc.dogettransaction(str(Leaderaddress),int(Leaderport),str(TXCOINHASH), str(TXADDRESS),str(TXMESSAGE)))
    		yield wfd
		res = str(wfd.getResult())
		wfd = defer.waitForDeferred(cc.doinitleader(str(Leaderaddress),int(Leaderport)))
    		yield wfd
		res = wfd.getResult()
		print "result-",res
		return

	@defer.deferredGenerator
	def generateht(self):
		# Once a hash table is copy the new peer will have to use it to generate its own hash table
		global FNAME
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		#conn,c=ht.connectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		guidlist = wfd.getResult()
		#guidlist=ht.getallguidht(c)
		for guid in guidlist:
			#address,port=ht.getaddress(c,guid)
			wfd = defer.waitForDeferred(ht.tgetaddress(dbpool,guid1))
			yield wfd
			address1,port1 = wfd.getResult()
			#guid1,d1,address,port=cc.getclosest(address,port,guid)
			wfd = defer.waitForDeferred(cc.getclosest(address,port,guid))
    			yield wfd
			data = str(wfd.getResult())
			# check to see if the guid exist if so do nothing
			#res=ht.checkguid(conn,c,guid1)
			wfd = defer.waitForDeferred(ht.tcheckguid(dbpool,guid1))
			yield wfd
			res = wfd.getResult()
			# else delete the guid and add guid1 to the hash table
			if (res==False):
				wfd = defer.waitForDeferred(ht.tdeleteht(dbpool,guid1))
				yield wfd
				#ht.deleteht(conn,c,guid1)
				time1=time.time()
				flag=0
				wfd = defer.waitForDeferred(ht.taddht(dbpool,guid1,address,port,flag,time1))
				yield wfd
				#ht.addht(conn,c,guid1,address,port,flag,time1)
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def sendcoin(self,guid,address,port,receiveraddress,coinhash,message):
		ut=utility(self.filename,self.address,self.port)
		time1=ut.gettimestamp()
		wfd = defer.waitForDeferred(cc.doencryptdata(address,port,str(coinhash)))
    		yield wfd
		signmessage1 = wfd.getResult()
		senderscript = str(coin)+" "+str(signmessage1)+" "
		receiverscript = " decode =  verify"
		transaction=tx.formattransaction(coinhash,senderscript,receiverscript,receiveraddress,message)
		txid=hashlib.sha1(transaction).hexdigest()
		cc.doacceptcoin(address,port,txid,transaction,receiveraddress,coinhash,time1)
		return

	@defer.deferredGenerator
	def generatenewcoin(self): #doacceptcoin(self,address,port,txid1,thash1,ts1)
		# will generate a new coin and give it to a random client
		global FNAME
		previoushash="00000000000000000000000000000000"
		ut=utility(self.filename,self.address,self.port)
		en= encyption()
		ht=hashtable()
		cc=clientcommands()
		gt=guidedtour()
		tx=transactions()
		time1=ut.gettimestamp()
		dbpool=ht.tconnectdb(FNAME)
		randaddress=ut.generateguid()
		coin=ut.generateguid()
		privkey=en.getprivatekey(FNAME)
		pubkey=en. getpublickey(FNAME)
		signmessage=en.signmessage(coin,privkey)
		# publickey = receiver public key
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		peerlist = wfd.getResult()
		guid,d2=ut.closestpeer(randaddress, peerlist)
		wfd = defer.waitForDeferred(ht.tgetaddress(dbpool,guid,d2))
		yield wfd
		data1 = wfd.getResult()
		address=str(data1[0])
		port=int(data1[1])
		ht.tclosedb(dbpool)
		wfd = defer.waitForDeferred(cc.dogetnewaddress(address,port,"newcoin"))
    		yield wfd
		receiveraddress = str(wfd.getResult())
		print "receiveraddress=",receiveraddress
		wfd = defer.waitForDeferred(cc.doencryptdata(address,port,str(coin)))
    		yield wfd
		signmessage1 = wfd.getResult()
		#signmessage1=en.encyptmessage(coin,publickey)
		senderscript = str(coin)+" "+str(signmessage1)+" "
		receiverscript = " decode =  verify"
		message="test"
		transaction=tx.formattransaction(previoushash,senderscript,receiverscript,receiveraddress,message)
		txid=hashlib.sha1(transaction).hexdigest()
		print "new coinhash - ",coin
		print "transaction - ",transaction
		print "txid - ",txid
		print "sending it to guid-"+guid+" at address-"+address+" port-"+str(port)
		cc.doacceptcoin(address,port,txid,transaction,receiveraddress,coin,time1)
		previousthash,lensender,senderscript,receiveraddress,lenreceiver,receiverscript,lenmessage,message = tx.decodetransaction(transaction)
		print "decoding transaction......."
		print "previoushash = ",previousthash
		print "lensender = ",lensender
		print "senderrscript = ",senderscript
		print "receiveraddress = ",receiveraddress
		print "lenreceiver = ", lenreceiver
		print "receiverscript = ",receiverscript
		print "lenmessage = ",lenmessage
		print "message = ",message
		# send this to the randaddress
		return

	@defer.deferredGenerator
	def checkblocktrans(txid):
		# check the network for updated transactions
		global FNAME,highestnumtb,updateaddress,updateport
		highestnumtb=0
		ht=hashtable()	
		cc=clientcommands()
		#conn,c=ht.connectdb(FNAME)
		dbpool=ht.tconnectdb(FNAME)
		#peerlist=ht.getallguidht(c)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		peerlist = wfd.getResult()
		for peer in peerlist:
			#address,port=ht.getaddress(c,peer)
			wfd = defer.waitForDeferred(ht.tgetaddress(dbpool,guid1))
			yield wfd
			address1,port1 = wfd.getResult()
			wfd = defer.waitForDeferred(cc.dogetnumtb(address,port))
    			yield wfd
			data = int(wfd.getResult())
			if (data>highestnumtb):
				highestnumtb=data
				updateaddress=self.address
				updateport=self.port
		ht.tclosedb(dbpool)
		# find the peer with the highest numtb and request update from that peer
		self.updateblocktrans(txid,updateaddress,updateport,highestnumtbnum)
		return

	@defer.deferredGenerator
	def updateblocktrans(txid,guid,address,port,num):
		# update transaction block with new txid
		global FNAME,highestnumtb,updateaddress,updateport
		cc=clientcommands()
		ht=hashtable()
		#conn,c=ht.connectdb(FNAME)
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tnumtb(dbpool))
    		yield wfd
		numtb = int(wfd.getResult())
		#numtb=ht.numtb(c)
		count1=0
		while (numtb<highestnumtb and count1<50):
		# find a way to loop through this to get all the updates
			wfd = defer.waitForDeferred(cc.doupdatetb(address,port))
    			yield wfd
			count+=1
			wfd = defer.waitForDeferred(ht.tnumtb(dbpool))
    			yield wfd
			numtb = int(wfd.getResult())
			#numtb=ht.numtb(c)
		ht.tclosedb(dbpool)
		return

class clientcommands:

	def __init__(self,filename,address,port):
      		self.filename = filename
      		self.address = address
		self.port = port

	def doping(self,address1,port1,guid):
		global GUID
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		pingDeferred = connectProtocol(destination, AMP())
		def connected(ampProto):
			print frm+" is sending a ping message to ",dest
        		return ampProto.callRemote(Ping, guid=GUID,address=self.address, port=self.port )
    		pingDeferred.addCallback(connected)
		def handleFailure(f):
			#would this be the best way.  will it block if it timeout?
    			print "errback"
    			print "we got an exception: %s" % (f.getTraceback(),)
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the ping message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
	    	pingDeferred.addErrback(handleFailure)
	    	def pinged(result):
			print frm+" has received a ping reply from ", dest
			print "result = ",result['reply']
			return result['reply']
	    	pingDeferred.addCallback(pinged)
		return pingDeferred
			
	def dodonetourguide(self,address1,port1):
		global GUID
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		donetourguideDeferred = connectProtocol(destination, AMP())
		def connected(ampProto):
			print frm+" is sending a donetourguide message to ",dest
        		return ampProto.callRemote(Donetourguide, guid=GUID,address=self.address, port=self.port )
    		donetourguideDeferred.addCallback(connected)
		def handleFailure(f):
    			print "errback"
    			print "we got an exception: %s" % (f.getTraceback(),)
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the ping message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
	    	donetourguideDeferred.addErrback(handleFailure)
	    	def donetourguideed(result):
			print frm+" has received a donetourguide reply from ", dest
			print "result = ",result['reply']
			return result['reply']
	    	donetourguideDeferred.addCallback(donetourguideed)
		return donetourguideDeferred

	def dogetguid(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getguidDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getguid message to ",dest
        		return ampProto.callRemote(Getuuid,guid=GUID,address=self.address,port=self.port)
    		getguidDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getguid message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getguidDeferred.addErrback(handleFailure)
    		def getguided(result):
			print frm+" has received a getguid reply from ", dest
			print "result = ", result['reply']
        		return result['reply']
    		getguidDeferred.addCallback(getguided)
		return getguidDeferred

	def docopyht(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		copyhtDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a copyht message to ",dest
        		return ampProto.callRemote(Copyht,guid=GUID,address=self.address,port=self.port)
    		copyhtDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the copyht message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		copyhtDeferred.addErrback(handleFailure)
    		def copyhted(result):
			print frm+" has received a copyht reply from ", dest
			print "result = ", result['reply']
			self.putdata(result['reply'])
        		return result['reply']
    		copyhtDeferred.addCallback(copyhted)
		return copyhtDeferred

	def dogetclosest(self,address,port,guid1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getclosestDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getclosest message to ",dest
        		return ampProto.callRemote(Getclosest,guid=guid1,address=self.address,port=self.port)
    		getclosestDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getclosest message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getclosestDeferred.addErrback(handleFailure)
    		def getclosested(result):
			print frm+" has received a getclosest reply from", dest
			print "result = ", result['reply']
        		return result['reply']
    		getclosestDeferred.addCallback(getclosested)
		return getclosestDeferred

	def dogetclosestpeer(self,address,port,guid1):
		global GUID
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getclosestpeerDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getclosestpeer message"
        		return ampProto.callRemote(Getclosest,guid=guid1,address=self.address,port=self.port)
    		getclosestpeerDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getclosestpeer message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getclosestpeerDeferred.addErrback(handleFailure)
    		def getclosestpeered(result):
			print frm+" has received a getclosestpeer reply ", result['reply']
        		return result['reply']
    		getclosestpeerDeferred.addCallback(getclosestpeered)

	def dosendtotg(self,address,port,hashvalue1,stopnumber1,length1,guid1,ts1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		sendtotgDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a sendtotg command to ",dest
        		return ampProto.callRemote(Sendtotg, hashvalue=hashvalue1, stopnumber=stopnumber1, length=length1,guid=guid1,ts=ts1,address=self.address,port=self.port)
    		sendtotgDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the sendtotg message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		sendtotgDeferred.addErrback(handleFailure)
    		def sendtotged(result):
			print frm+" has received a sendttg reply from ", dest
			print "result = ",result['reply']
        		return result['reply']
    		sendtotgDeferred.addCallback(sendtotged)
		return sendtotgDeferred

	def dosendpublickey(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		sendpublickeyDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a sendpublic message to ",dest
        		return ampProto.callRemote(Sendpublickey,guid=GUID,address=self.address,port=self.port)
    		sendpublickeyDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the sendpublic message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		sendpublickeyDeferred.addErrback(handleFailure)
    		def sendpublickeyed(result):
			print frm+" has received a sendpublic reply from ",dest
			print "result =",result['reply']
        		return result['reply']
    		sendpublickeyDeferred.addCallback(sendpublickeyed)
		return sendpublickeyDeferred

	def dogetnumtb(self,address,port):
		global GUID
		frm=str(self.address)+":"+str(self.port)
		dest=str(address)+":"+str(port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getnumtbDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getnumtb message to ",dest
        		return ampProto.callRemote(Getnumtb,guid=GUID,address=self.address,port=self.port)
    		getnumtbDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getnumtb message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getnumtbDeferred.addErrback(handleFailure)
    		def getnumtbed(result):
			print frm+" has received a getnumtb reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		getnumtbDeferred.addCallback(getnumtbed)
		return getnumtbDeferred

	def dogetnewaddress(self,address,port,account1):
		global GUID
		frm=str(self.address)+":"+str(self.port)
		dest=str(address)+":"+str(port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getnewaddressDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getnewaddress message to ",dest
        		return ampProto.callRemote(Getnewaddress,guid=GUID,address=self.address,port=self.port,account=account1)
    		getnewaddressDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getnewaddress message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getnewaddressDeferred.addErrback(handleFailure)
    		def getnewaddressed(result):
			print frm+" has received a getnewaddres reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		getnewaddressDeferred.addCallback(getnewaddressed)
		return getnewaddressDeferred

	def doencryptdata(self,address,port,data1):
		global GUID
		frm=str(self.address)+":"+str(self.port)
		dest=str(address)+":"+str(port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		encryptdataDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a encryptdata message to ",dest
        		return ampProto.callRemote(Encryptdata,guid=GUID,address=self.address,port=self.port,data=data1)
    		encryptdataDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the encryptdata message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		encryptdataDeferred.addErrback(handleFailure)
    		def encryptdataed(result):
			print frm+" has received a encryptdata reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		encryptdataDeferred.addCallback(encryptdataed)
		return encryptdataDeferred

	def doupdatetb(self,address,port,thash1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		updatetbDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a updatetb message to ",dest
        		return ampProto.callRemote(Updatetb,thash=thash1,guid=GUID,address=self.address,port=self.port)
    		updatetbDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the updatetb message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		updatetbDeferred.addErrback(handleFailure)
    		def updatetbed(result):
			# store transaction and repeat if necessay
			print frm+" has received an updatetb reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		updatetbDeferred.addCallback(updatetbed)
		return updatetbDeferred

	def doboardcasttrans(self,address,port,txid1,thash1,ts1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		boardcasttransDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a boardcasttrans message to ",dest
        		return ampProto.callRemote(Boardcasttrans,txid=txid1,thash=thash1,ts=ts1,guid=GUID, address=self.address,port=self.port)
    		boardcasttransDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the boardcasttrans message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		boardcasttransDeferred.addErrback(handleFailure)
    		def boardcasttransed(result):
			print frm+" has received a boardcasttrans reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		boardcasttransDeferred.addCallback(boardcasttransed)
		return boardcasttransDeferred

	def dogeneratecoin(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		generatecoinDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a generatecoin message to ",dest
        		return ampProto.callRemote(Generatecoin,guid=GUID,address=self.address,port=self.port)
    		generatecoinDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the generatecoin message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		generatecoinDeferred.addErrback(handleFailure)
    		def generatecoined(result):
			print frm+" has received a generatecoin reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		generatecoinDeferred.addCallback(generatecoined)
		return generatecoinDeferred

	def doacceptcoin(self,address,port,txid1,thash1,ts1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		acceptcoinDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a acceptcoin message to ",dest
        		return ampProto.callRemote(Acceptcoin,txid=txid1,thash=thash1,ts=ts1,guid=GUID, address=self.address,port=self.port)
    		acceptcoinDeferred.addCallback(connected)
		def handleFailure(f):
			# have to add reset tour because if it reach here than something went wrong with the tour
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the acceptcoin message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		acceptcoinDeferred.addErrback(handleFailure)
    		def acceptcoined(result):
			print frm+" has received an acceptcoin reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		acceptcoinDeferred.addCallback(acceptcoined)
		return acceptcoinDeferred

	def dogetleader(self,address1,port1,guid1):
		global GUID
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		getleaderDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getleader message to ",dest
        		return ampProto.callRemote(Getleader,clientaddress=self.address1,clientport=self.port1,guid=guid1,address=self.address,port=self.port)
    		getleaderDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getleader message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getleaderDeferred.addErrback(handleFailure)
    		def getleadered(result):
			print frm+" has received a getleader reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		getleaderDeferred.addCallback(getleadered)
		return getleaderDeferred

	def dosetleader(self,address1,port1,clientaddress1,clientport1,guid1):
		global self.filename,self.address,self.port
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		setleaderDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a setleader message to ",dest
        		return ampProto.callRemote(Setleader,clientaddress=clientaddress1,clientport=clientport1,guid=guid1,address=self.address,port=self.port)
    		setleaderDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the setleader message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		setleaderDeferred.addErrback(handleFailure)
    		def setleadered(result):
			print frm+" has received a setleader reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		setleaderDeferred.addCallback(setleadered)
		return setleaderDeferred

	def dosendtransaction(self,address1,port1,coinhash1,receiveraddress1,message1):
		global GUID
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		sendtransactionDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a sendtransaction message to ",dest
        		return ampProto.callRemote(Sendtransaction,guid=GUID,address=self.address1,port=self.port1,coinhash=coinhash1, receiveraddress=receiveraddress1, message=message1)
    		sendtransactionDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the sendtransaction message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		sendtransactionDeferred.addErrback(handleFailure)
    		def sendtransactioned(result):
			print frm+" has received a sendtransaction reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		sendtransactionDeferred.addCallback(sendtransactioned)
		return sendtransactionDeferred

	def dogettransaction(self,address1,port1):
		global GUID
		dest=str(address1)+":"+str(port1)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address1, port1)
    		gettransactionDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a gettransaction message to ",dest
        		return ampProto.callRemote(Gettransaction,guid=GUID,address=self.address1,port=self.port1)
    		gettransactionDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the gettransaction message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		gettransactionDeferred.addErrback(handleFailure)
    		def gettransactioned(result):
			print frm+" has received a gettransaction reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		gettransactionDeferred.addCallback(gettransactioned)
		return gettransactionDeferred

	def dogetpuzzle(self,address,port,guid1,h01,ts1,L1,arraytg1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
		# h0,ts,L,arraytg
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		getpuzzleDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a getpuzzle message to ",dest
        		return ampProto.callRemote(Getpuzzle,guid=guid1,h0=h01,ts=ts1,L=L1,arraytg=arraytg1,guid1=GUID, address=self.address,port=self.port)
    		getpuzzleDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the getpuzzle message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		getpuzzleDeferred.addErrback(handleFailure)
    		def getpuzzleed(result):
			print frm+" has received a getpuzzle reply from ",dest
			print "result = ", result['reply']
        		return result['reply']
    		getpuzzleDeferred.addCallback(getpuzzleed)
		return getpuzzleDeferred

	def doverifypuzzle(self,address,port,guid1,h01,hl1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		verifypuzzleDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a verifypuzzle message to ",dest
        		return ampProto.callRemote(Verifypuzzle,guid=guid1,h0=h01,hl=hl1,address=self.address,port=self.port)
    		verifypuzzleDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the verifypuzzle message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		verifypuzzleDeferred.addErrback(handleFailure)
    		def verifypuzzleed(result):
			print frm+" has received a verifypuzzle reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		verifypuzzleDeferred.addCallback(verifypuzzleed)
		return verifypuzzleDeferred

	def doleaderinfo(self,address,port,guid1,address1,port1):
		global GUID
		frm=str(self.address)+":"+str(self.port)
		dest=str(address)+":"+str(port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		leaderinfoDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a leaderinfo message to ",dest
        		return ampProto.callRemote(Leaderinfo,guid=guid1,address=self.address1,port=self.port1)
    		leaderinfoDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the leaderinfo message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		leaderinfoDeferred.addErrback(handleFailure)
    		def leaderinfoed(result):
			print frm+" has received a leaderinfo reply frm ",dest
			print "result - ",result['reply']
        		return result['reply']
    		leaderinfoDeferred.addCallback(leaderinfoed)
		return leaderinfoDeferred

	def doinitleader(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		initleaderDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a initleader message to ",dest
        		return ampProto.callRemote(Initleader,message='init',guid=GUID,address=self.address,port=self.port)
    		initleaderDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the initleader message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		initleaderDeferred.addErrback(handleFailure)
    		def initleadered(result):
			print frm+" has received an initleader reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		initleaderDeferred.addCallback(initleadered)
		return initleaderDeferred

   	def doleave(self,address,port,guid1):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		leaveDeferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a leave message to ",dest
        		return ampProto.callRemote(Leave,guid=guid1,address=self.address,port=self.port)
    		leaveDeferred.addCallback(connected)
		def handleFailure(f):
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the leave message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			return False
    		leaveDeferred.addErrback(handleFailure)
    		def leaveed(result):
			print frm+" has received a leave reply from ",dest
			print "result = ",result['reply']
        		return result['reply']
    		leaveDeferred.addCallback(leaveed)
		return leaveDeferred

	def dojoin(self,address,port):
		global GUID
		dest=str(address)+":"+str(port)
		frm=str(self.address)+":"+str(self.port)
    		destination = TCP4ClientEndpoint(reactor, address, port)
    		join1Deferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a join message (getguid) to ",dest
        		return ampProto.callRemote(Getuuid,guid=GUID,address=self.address,port=self.port)
    		join1Deferred.addCallback(connected)
		def handleFailure(f):
			# have to add another peer to request information from
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the join (getguid) message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			print "no reply from the getguid message"
			return False
    		join1Deferred.addErrback(handleFailure)
    		def join1ed(result):
			print frm+" has received a join reply (getguid) from ", dest
			print "result = ",result['reply']
        		return result['reply']
    		join1Deferred.addCallback(join1ed)
    		join2Deferred = connectProtocol(destination, AMP())
    		def connected(ampProto):
			print frm+" is sending a join message (copydb) to ",dest
        		return ampProto.callRemote(Copyht,guid=GUID,address=self.address,port=self.port)
    		join2Deferred.addCallback(connected)
		def handleFailure(f):
			# have to add another peer to request information from
    			f.trap(RuntimeError)
			ut=utility(self.filename,self.address,self.port)
			message = "no reply from the join (copydb) message"
			ut.messagefail(message, guid)
			ut.updateflag(guid)
			print "no reply from the copyht message"
			return False
    		join2Deferred.addErrback(handleFailure)
    		def join2ed(result):
			print frm+" has received a join reply (copydb) from ", dest
			print "result = ",result['reply']
        		return result['reply']
    		join2Deferred.addCallback(join2ed)
    		def done(result):
        		print 'Done with join message. reply:', result
    		defer.DeferredList([join1Deferred, join2Deferred]).addCallback(done)
		return defer.DeferredList

	@defer.deferredGenerator	
	def putdata(self,data):
		# put data received into database guid text, address text, port integer, flag integer, time real
		# might want to put this with the command block for struture reason
		global FNAME
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		rows=data.split(":")
		for i in rows:
			row=i.split(",")
			guid=row[0]
			address=row[1]
			port=row[2]
			flag=row[3]
			time1=row[4]
			wfd = defer.waitForDeferred(ht.taddht(dbpool,str(guid),str(address),int(port),int(flag),float(time1)))
			yield wfd	
		return

class guidedtour:

	# Length of tour
	MAXL = 10
	MINL = 5
	# Number of tour guides
	MAXTG = 10
	MINTG = 5
	# Tour Guide list [guid,ks]
	tglist=[]

	def __init__(self,filename,address,port):
      		self.filename = filename
      		self.address = address
		self.port = port

	def getlength(self):
		# L length of the tour
		L=random.randint(self.MINL,self.MAXL)
		return L

	def gettourguides(self):
		# The tour guides will be chosen from the leaders hash table
		# A suitable range of tour guides will be determine
		# process for the leader to choose the tour guides
		# 1) The leader will randomly choose the number of tour guides from its hash table (N)
		# 2) The leader will send a request for a secret key from each of its tour guide 
		# 3) The address and secret key from each tour guide will be stored in an array (TG)
		# Do not need this method anymore!!!!!
		gtlist=[]
		N=random.randint(self.MINTG,self.MAXTG)
		ht=hashtable()
		conn,c=ht.connectdb(self.filename)
		peerlist=ht.getallguidht(c)
		count1=ht.numht(c)
		print "peerlist=",peerlist
		for i in range(1,N):
			gt = random.randint(0,count1-1)
			print "gt=",gt
			gtlist.append(peerlist[gt])
		return gtlist

	def getleader(self):
		# process to find leader:
		# 1) The client peer will generate a random guid 
		# 2) The client will send a request to the peer the is closest to this random guid
		# 3) That second peer will generate another random guid and send a request to the closest peer to this guid
		# 4) This third peer will become the leader and send back to the second peer a secret key
		# 5) This secret key, leader's address and its guid will be sent back to the client 
		# 6) The client will than send the secret key and client guid to the leader to initiate the guided tour
		ut=utility(self.filename,self.address,self.port)
		zt=Zeit()
		guid = ut.generateguid()
		guid1,address,port = zt.getclosestpeer(guid)
		# a command that tells guid1 to choose a leader (maybe use a hash to make sure it came from guid1
		return

	def sendpuzzle(self):
		global Clientaddress,Clientport,Clientguid,GTlist
		cc=clientcommands() 
		en=encyption()
		ks=en.getpublickey(self.filename)
		L=self.getlength()
		ts=self.gettimestamp()
		h0=self.makepuzzle(Clientguid,L,ts,ks)
		cc.dogetpuzzle(Clientaddress,int(Clientport),Clientguid,h0,ts,L,GTlist)
		#cc.dogetpuzzle('127.0.0.1',1234,'1111','ho1111111',1111.22,5,'arr1arr2')
		return

	def makepuzzle(self,guid,L,ts,ks):
		# h_{0} = hash(A_{x}\; ||\; L\; ||\; ts\; ||\; K_{s})
		# Ax - guid of the client
		# hash - a hash function will use sha1
		# will send back h0, L, array of tour guides address
		# will have to figures out ts (coarse timestamp)
		data1=str(guid)+":"+str(L)+":"+str(ts)+":"+str(ks)
		puzzle=hashlib.sha256(data1).hexdigest()
		return puzzle

	def getpuzzle(self,guid,h0,ts,L,arraytg):
		# store the data locally for use bt the client for the tour
		global Leaderaddress, Leaderport
		tourlist=[]
		print "Data has been received for the tour guid-"+guid+" h0-"+h0+" ts-"+str(ts)+" L-"+str(L)+" arraytg-"+arraytg
		list1=arraytg.split(":")
		for line in list1:
			list2=line.split(",")
			print "list2=",list2
			tourlist.append(list2)
		self.runtour(h0,L,Leaderaddress,Leaderport,guid,ts,tourlist)
		return

	def gettourindex(self,hashvalue,N):
		# S_{l}=(h_{l-1}\; mod\; N)
		# h_{l} = hash(h_{l-1}\; ||\; l\; ||\; L\; ||\; A_{x}\; ||\; ts\; ||\; k_{js}) 
		# N - number of tour guides
		tourindex = long(hashvalue,16) % int(N)
		return tourindex

	def sendtoguide(hashvalue,stopnumber,L):
		return

	@defer.deferredGenerator
	def runtour(self,h0,L,leaderaddress,leaderport,clientguid,ts,tourlist):
		hi=h0
		cc=clientcommands()
		for l in range(1,int(L)):
			tourindex=self.gettourindex(h0,len(tourlist))
			print "tourindex=",tourindex
			print "l=",l
			print "tourlist=",tourlist[int(l)]
			wfd = defer.waitForDeferred(cc.dosendtotg(tourlist[l][1],int(tourlist[l][2]),hi,l,L,clientguid,ts))
    			yield wfd
			hi = str(wfd.getResult())
		wfd = defer.waitForDeferred(cc.doverifypuzzle(leaderaddress,leaderport,clientguid,h0,hi))
		yield wfd
		result = wfd.getResult()
		if (result):
			# store transaction and boardcast
			# send the result back to the client so it can do the same
			print "The puzzle is good"
		else:
			# send a message to the client to rerun the tour 
			print "The puzzle is no good"
		return

	def tourguideverify(self,hashvalue,stopnumber,length,guid,ts):
		en = encyption()
		ks=en.getpublickey() 
		hashstr=str(hashvalue)+":"+str(stopnumber)+":"+str(length)+":"+str(guid)+":"+str(ts)+":"+str(ks)
		print "hashstr=",hashstr
		result=hashlib.sha256(hashstr).hexdigest()
		return result

	def finishtour(self,firsthash,lasthash):
		# cleanup the tour	
		return

	def verifypuzzle(self,guid,firsthash,lasthash):
		# leader table that holds: sharedkeys, address, port, guid, timestamp
		# might want to move this to a tread
		# Retrieve L, ts and clientguid from storage
		# Do not need this method anymore
		flag=0
		keylist=[]
		h0=firsthash
		ht=hashtable()
		N=ht.numtg()
		keyslist=ht.getkeys()
		for i in range(0,L):
			tourindex=self.gettourindex(h0,N)
			key=keylist[tourindex]
			h0=self.tourguideverify(h0,i+1,L,clientguid,key,ts)
		ht.deleteleader()
		if (h0==lasthash):
			result=True
			#store the transaction and boardcast it
		else:
			result=False
		return result

	def gettimestamp(self):
		# Ts course timestamp
		time1=time.time()
		return time1

	@defer.deferredGenerator
	def getsharedsecret(self,gtlist):
		# Ks short live secret
		global GTlist
		ht=hashtable()
		cc=clientcommands()
		gt=guidedtour()
		timestamp=self.gettimestamp()
		dbpool=ht.tconnectdb(self.filename)
		#conn,c=ht.connectdb(FNAME)
		for guid in gtlist:
			wfd = defer.waitForDeferred(ht.tgetaddress(dbpool,guid1))
			yield wfd
			address1,port1 = wfd.getResult()
			#address,port=ht.getaddress(c,guid)
			GTlist=GTlist+str(guid)+","+str(address)+","+str(port)+":"
			# do sentpubkey
			#sharedkey=cc.dosendpublickey(address,port)
			wfd = defer.waitForDeferred(cc.dosendpublickey(address,port))
    			yield wfd
			sharedkey = str(wfd.getResult())
			# store the secret key in the local database
			wfd = defer.waitForDeferred(ht.taddleader(dbpool,sharedkey, address, port, guid, timestamp))
			yield wfd
			#ht.addleader(conn,c,sharedkey, address, port, guid, timestamp)
		GTlist=GTlist[:-1]
		gt.sendpuzzle()
		return

class controller: # this works yeah

	# every hour ping to say i am still coonected to the nextwork
	# every hour do an update transaction request
 	# every dat post to the websites for bootstrapping/peer location (also when first jogging into the network)

	def __init__(self,filename,address,port):
      		self.filename = filename
      		self.address = address
		self.port = port

	def startupdatetranstimer(self):
		t = task.LoopingCall(self.dotimedping)
		t.start(20) # call every 3600 seconds = hour
		# l.stop() will stop the looping calls
		return t

	def stopupdatetranstimer(t):
		t.stop()
		return t

	@defer.deferredGenerator
	def dotimedupdatetrans(self):
		# might have to lock database to make sure data is not corrupted
  		#threading.Timer(5.0, timedping).start()
		# might want to limit the amount of opem connection to some maxvalue
  		print "Update Transaction Block timer event"
		cc=clientcommands()
		ht=hashtable()
		dbpool=ht.tconnectdb(self.filename)
		#conn,c=ht.connectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		guidlist = wfd.getResult()
		#guidlist = ht.getallguidht(c)
		for guid in guidlist:
			address,port=ht.getaddress(c,guid)
			wfd = defer.waitForDeferred(cc.doping(address,port,guid))
			yield wfd
			result = cc.doping(str(address),int(port),guid)
		ht.tclosedb(dbpool)
		return 

	def startpingtimer(self):
		t = task.LoopingCall(self.dotimedping)
		t.start(20) # call every 3600 seconds = hour
		# l.stop() will stop the looping calls
		return t

	def stoppingtimer(t):
		t.stop()
		return t

	
	@defer.deferredGenerator
	def dotimedping(self):
		# might have to lock database to make sure data is not corrupted
  		#threading.Timer(5.0, timedping).start()
		# might want to limit the amount of opem connection to some maxvalue
  		print "Update Ping timer event"
		cc=clientcommands()
		ht=hashtable()
		dbpool=ht.tconnectdb(self.filename)
		#conn,c=ht.connectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
		yield wfd
		guidlist = wfd.getResult()
		#guidlist = ht.getallguidht(c)
		for guid in guidlist:
			address,port=ht.getaddress(c,guid)
			wfd = defer.waitForDeferred(cc.doping(address,port,guid))
			yield wfd
			result = cc.doping(str(address),int(port),guid)
		ht.closedb(conn)
		return 

	def timedping(self):
		reactor.callInThread(self.dotimedping)
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
	print "99) to see the menu"
	

def startservers(): 
        # Start the amp server
        global PORT
        port1=raw_input("What port do you want the amp server to listen?\n")
        PORT=int(port1)
        pf = Factory()
        pf.protocol = Zeit
        reactor.listenTCP(PORT, pf)
        print "AMP servers has started ...."

@defer.deferredGenerator
def docommand(str1):
	global ALIVE
	arglist=[]
	cc=clientcommands(FNAME,ADDRESS,PORT)
    	ut=utility(FNAME,ADDRESS,PORT)
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
	if (com1=="0"):
		ALIVE=0
		print "Quiting..."
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
			str1=str(com1)+":"+str(self.address)+":"+str(self.port)
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

def main():
	print "Testing platform for the zeitcoin network"
	startservers()
	printmenu()
	runinput()
	reactor.run()
	sys.exit(0)
	
if __name__ == '__main__':
    main()
