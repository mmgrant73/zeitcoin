#!/usr/bin/env python
#########################################
# Zeitcoin Transaction Class
#########################################

import sys
from zeitcoindb import hashtable
from zeitcoinutility import utility,encyption

class transactions:
	# Will handle transactions
	# Transaction (format)
	# | Previous hash value (32 bytes)| length of sender script (4 bytes) | sender script | receiver address (32 bytes) 		# | length of receiver script (4 bytes) | receiver script | length of optional message (4 bytes) | message |

	# Transaction Block Table: 
	# thash - hash of the transaction (32 byte hash)
	# transactionscript - The whole formated transaction as listed above
	# timestamp - the time the transaction was received 

	def __init__(self,filename,address,port):
      		self.filename = filename
      		self.address = address
		self.port = port

	def decodetransaction(self,thash):
		previousthash=thash[:32]
		hexlensender=thash[32:36]
		lensender = int(hexlensender, 16)*2
		senderscript=thash[36:36+lensender]
		receiveraddress=thash[36+lensender:68+lensender]
		hexlenreceiver=thash[68+lensender:72+lensender]
		#print "hexlenreceiver = ", hexlenreceiver
		lenreceiver=int(hexlenreceiver,16)*2
		receiverscript=thash[72+lensender:72+lensender+lenreceiver]
		hexlenmessage=thash[72+lensender+lenreceiver:76+lensender+lenreceiver]
		lenmessage=int(hexlenmessage,16)*2
		message=thash[76+lensender+lenreceiver:76+lensender+lenreceiver+lenmessage]
		return previousthash,lensender,senderscript.decode("hex"), receiveraddress,lenreceiver,receiverscript.decode("hex"), lenmessage,message.decode("hex")

	def formattransaction(self,previousthash,senderscript,receiverscript,receiveraddress,message):
		lpreviousthash=len(previousthash)
		if (lpreviousthash!=32):
			print "[Error] - The previous thash is not a valid 32 byte hash"
		lreceiveraddress=len(receiveraddress)
		if (lreceiveraddress!=32):
			print "[Error] - The receiver address is not a valid zietcoin address"
		lensender=len(senderscript)
		if (lensender>4294967296):
			print "[Error] - The sender script is too long"
		lenreceiver=len(receiverscript)
		if (lenreceiver>4294967296):
			print "[Error] - The receiver script is too long"
		lenmessage=len(message)
		if (lenmessage>4294967296):
			print "[Error] - The message is too long"
		lsender = self.formatint2hex(lensender,4)
		lreceiver = self.formatint2hex(lenreceiver,4)
		lmessage = self.formatint2hex(lenmessage,4)
		hexsender=self.formatstr2hex(senderscript)
		hexreceiver=self.formatstr2hex(receiverscript)
		hexmessage=self.formatstr2hex(message)
		print "lsender for tx = ",lsender
		print "hexsender for tx = ",hexsender
		print "address for tx = ",receiveraddress
		print "lreceiver for tx = ",lreceiver
		print "hexreceiver for tx = ",hexreceiver
		print "lmessage for tx = ",lmessage
		print "hexmessage for tx = ",hexmessage
		transaction=str(previousthash)+str(lsender)+str(hexsender)+str(receiveraddress)+str(lreceiver)+str(hexreceiver)+str(lmessage)+str(hexmessage)
		return transaction

	def formatint2hex(self,int1,fill):
		hex1=format(int(int1),'x')
		hex1=hex1.zfill(fill)
		return hex1

	def formatstr2hex(self,str1):
		hexstr=''
		for c in str1:
			int1=ord(c)
			hex1 = self.formatint2hex(int1,2)
			hexstr+=hex1
		return hexstr

	def getreceivedcoins(self):
		# Go throught the transaction block and find all coins owned by the wallet with a certain guid
		# will return the number of coins that can be sent by the owner of the wallet
		# probably will want to do this method in a thread as it might take a long time
		ht=hashtable()
		dbpool=ht.tconnectdb(self.filename)
		d = defer.Deferred()
		d.addCallback(ht.tgetalltb)
		d.addCallback(ht.tgetallaccount)
		d.addCallback(self._getreceivedcoins,ht,dbpool) 
		d.callback(dbpool)
		return

	def _getreceivedcoins(self,tblist,accountlist):
		coinlist=[]
		for tx in tblist:
			previousthash,lensender,senderscript, receiveraddress,lenreceiver,receiverscript, lenmessage, message = self.decodetransaction(tx[1])
			for a in account:
				if (a[0]==receiveraddress):
					list1=[]
					list1.append(receiveraddress)
					list1.append(a[3])
					list1.append(tx[0])
					coinlist.append(list1)
		return coinlist

	def getunspentcoins(self, coinlist,tblist):
		# Will go throught the transaction block and find all the coins that can be spent by the wallet
		# Will return the thast of all the coins that is owned
		# probably will want to do this method in a thread due to the time it might take
		coinlist1=[]
		for tx in tblist:
			previousthash,lensender,senderscript, receiveraddress,lenreceiver,receiverscript, lenmessage, message = self.decodetransaction(tx[1])
			flag=0
			for c in coinlist:
				if (c[2]==previousthash):
					flag=1
			if flag==0:
				coinlist1.append(c)
		return coinlist1

	def getaddressofsender(self,thash,tblist):
		# Will go through the transaction block and return the address of the sender of that thash (thread)
		previousthash1,lensender,senderscript, receiveraddress,lenreceiver,receiverscript, lenmessage,message = self.decodetransaction(thash)	
		for tx in tblist:
			if (tx[0]==previousthash):
				previousthash,lensender,senderscript, receiveraddress,lenreceiver,receiverscript, lenmessage,message = self.decodetransaction(tx)
				break;
		return receiveraddress

	def getaddressofreceiver(self,thash):
		# Will go through the transaction block and return the receiver address of a thash (thread)
		previousthash1,lensender,senderscript, receiveraddress,lenreceiver,receiverscript, lenmessage,message = self.decodetransaction(thash)
		return receiveraddress

	def receivedtrans(self,coinhash,receiveraddress,message):
		# received a new transaction from a person trying to send a coin
		# will call sendcoin after the client finish the guided tour
		return

	def sendtrans(self):
		# send a transaction to the network
		return

	def sendcoin(self,coinhash,receiveraddrress,message):
		# send a coin to a certain address
		# check to make sure this wallet owns this coin
		# receiveraddress - first 32 bytes wallet guid | last 32 bytes will be the address that is stored in tb
		# get the wallet guid and get its address and port
		# zt=Zeit()
		# zt=sendcoin(address,port,receiveraddress,coinhash,message)
		return 

	def hashtransaction(self,tx):
		# format a transaction
		result=hashlib.sha256(tx).hexdigest()
		return result
	
	def checkvalidtx(self,receiveraddress,senderaddress,previoushash,txid,thash):
		# Create local transaction list that holds: txid, thash, addresswallet,addressother, amount, timestamp
		# check if the sender the valid owner of the coin 
		# check to see if the previous hash exist
		# Check to see if the transaction is valid over-all. 
		return
	
	def checktransaction(self,inputtx,outputtx):
		# check the input and output side of the transaction (returns true or false)
		result==False
		zf=zietforth()
		res1=zf.execute(inputtx)
		res2=zf.execute(outputtx)
		if (res1==True and res2==True):
			result=True
		return result

	def broadcasttrans(self,txid,thash,ts):
		# broadcast a valid transaction to all nodes
		# node that did the transaction will broadcast to everyone on its hash table.
		# everyone that receive this broadcast will rebroadcast to its farest peer and its closest peer
		ut=utility(self.filename,self.address,self.port)
		ut.boardcasttrans(txid,thash,ts)
		return

	def acceptcoin(self,txid,thash,addresswallet,addressother,timestamp):
		# store it in the local transaction table
		# update balance txid,thash,addresswallet,addressother,amount,type1,time1
		amount=1
		type1="received"
		self.storetransaction(txid,thash,addresswallet,otheraddress,amount,type1,timestamp)
		print "new coin was accepted with txid="+str(txid)+" thash="+thash+" ts="+str(timestamp)
		return

	def storetransaction(self,txid,thash,addresswallet,otheraddress,amount,type1,timestamp):
		# store the transaction in the database 
		global FNAME
		ht=hashtable()
		#conn,c=ht.connectdb(FNAME)
		dbpool=ht.tconnectdb(FNAME)
		#ht=addtb(conn,c,txid,thash,time1)
		wfd = defer.waitForDeferred(ht.taddtb(dbpool,txid,thash,timestamp))
    		yield wfd
		wfd = defer.waitForDeferred(ht.taddlt(dbpool,txid,thash,addresswallet,addressother,amount,type1,timestamp))
    		yield wfd #tgetnewbalance(self,dbpool)
		wfd = defer.waitForDeferred(ht.tgetnewbalance(dbpool))
    		yield wfd
		balance = wfd.getResult()
		wfd = defer.waitForDeferred(ht.tupdatebalance(self,dbpool,balance,guid))
    		yield wfd #tupdatebalance(self,dbpool,balance,guid)
		ht.tclosedb(dbpool)
		return

def main():
	print "Testing the Transaction class"
	sys.exit(0)
	
if __name__ == '__main__':
    main()

#Generation of new coin:

#senderscript:
#push signcoinhash - sign the coinhash with the peer generating the key private key
#push publickey    - public key from the peer generating the coin
#verifysign

#receiveraddress - guid of receiver:account address

#receiverscript:
#push coinhash - getguid
#push signcoinhash1 - sign with receiver of the coin public key
#decode signcoinhash1
#eq signcoinhash1 = decodecoinhash
#and 1 and 1
#verify

#push signcoinhash			[signcoinhash]
#push publickey				[signcoinhash, publickey]
#versign signcoinhash and pubkey	[true]
#push coinhash				[true,coinhash]
#push signcoinhash1			[true, coinhash, signcoinhash1]
#decode signcoinhash1			[true, coinhash, decodecoinhash]
#eq coinhash=decodecoinhash		[true, true]
#and (1 and 1)				[true]
#verify return true			[]

#============================================================================

#push coinhash				[coinhash]
#push signcoinhash			[coinhash, signcoinhash]
#decode signcoinhash			[coinhash, decodecoinhash]
#eq coinhash = decodecoinhash		[true]
#verify					[]

