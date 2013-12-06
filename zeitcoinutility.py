#!/usr/bin/env python
############################################
# Zeitcoin Utility, Log and Encyption Class
############################################

import uuid, time, hashlib, shutil, random, os, sys
from M2Crypto import Rand, RSA, BIO, EVP
from twisted.internet import defer
from zeitcoindb import hashtable
from twisted.web.client import getPage
from twisted.internet import reactor

ADDRESS='127.0.0.1'
FNAME='zeitcoin'
PORT=1234

class utility:

	def __init__(self,filename,address,port):
      		self.filename = filename
      		self.address = address
		self.port = port

	def generateguid(self):
		guid=str(uuid.uuid4())
		guid=guid.replace("-","")
        	#print 'Getuuid: = %s' % (guid)
		return guid

	def getdistance(self,peer1,peer2):
		# Will use Kademlia's Distance Function as it seems to be the best way of getting 
		# distance between peers compared to others such as Chord, Pastry and Tapestry
		# Kademlia's Distance Function is defined as [distance = peer1 XOR peer2]
		p1=long(peer1,16)
		p2=long(peer2,16)
		distance=p1^p2
		return distance

	def backupwallet(self,backupname):
		shutil.copy2('zeitcoin.db', backupname)
		return

	def checkpeer(self, guid, address, port):
		# already did this damn it db - checkguid REDUNTANT
		ht=hashtable()
		time1=self.gettimestamp()
		flag=0
		dbpool=ht.tconnectdb(self.filename)
		#conn,c=ht.connectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tcheckguid(dbpool,guid))
		yield wfd
		data1 = wfd.getResult()
		wfd = defer.waitForDeferred(ht.tcheckpeer(dbpool,guid,address,port))
		yield wfd
		data2 = wfd.getResult()
		if (data1==True and data2==True):
			wfd = defer.waitForDeferred(ht.tupdatetime(dbpool,guid))
			yield wfd
		elif (data1==False and data2==False):
			wfd = defer.waitForDeferred(ht.taddht(dbpool,guid,address,port,flag,time1))
			yield wfd
		else:
			wfd = defer.waitForDeferred(ht.tupdatepeer(self,dbpool,guid,address,port))
			yield wfd
		ht.tclosedb(dbpool)
		return #result

	@defer.deferredGenerator
	def messagefail(self,message, guid):
		print message
		ht=hashtable()
		dbpool=ht.tconnectdb(self.filename)
		wfd = defer.waitForDeferred(ht.tdeleteht(dbpool,guid))
		yield wfd
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def updatepeer(self,guid,address,port):
		ht=hashtable()
		time1=self.gettimestamp()
		dbpool=ht.tconnectdb(self.filename)
		wfd = defer.waitForDeferred(ht.tcheckguid(dbpool,guid))
		yield wfd
		check1 = wfd.getResult()
		if (check1==True):
			# Check to see if peer exist in hastable if so update flag and timestamp
			print "the peer already exist in the hasttable, updating flag and timestamp"
			wfd = defer.waitForDeferred(ht.tupdatepeer(dbpool,guid,address,port))
			yield wfd
		else:
			# else check if hashtable is full more than 128 peers
			print "the peer is not in the hashtable"
			wfd = defer.waitForDeferred(ht.tcheckfullht(dbpool))
			yield wfd
			check2 = wfd.getResult()
			if (check2==False):
				print "The hash table is not full"
				# if not than add the new peer to the hash table
				wfd = defer.waitForDeferred(ht.taddht(dbpool,guid,address,port,'1',time1))
				yield wfd
			else:
				# if so check for inactive guid (peers)
				wfd = defer.waitForDeferred(ht.tgetflag(dbpool))
				yield wfd
				guid1 = wfd.getResult()
				if (guid1 != '0'):
					print "deleting an inactive peer with the oldest timestamp"
					# delete an inactive guid the one with the earliest timestamp and add new peer
					wfd = defer.waitForDeferred(ht.tdeleteht(dbpool,guid))
					yield wfd
					wfd = defer.waitForDeferred(ht.taddht(dbpool,guid,address,port,'1',time1))
					yield wfd
				else:
					# if there is none inactive than check if this one is closer than the farest peer
					# if so replace the farest with the new peer else just drop this peer
					print "There is no inactive peer"
					wfd = defer.waitForDeferred(ht.tgetallguidht(dbpool))
					yield wfd
					peerlist = wfd.getResult()
					self.farestpeer(peerid, peerlist)
					# have to think about this
		ht.tclosedb(dbpool)
		return

	def updateflag(self, guid):
		# update the flag in the hash table to 0 = inactive which will be replaced by new entries to the table
		ht=hashtable()
		flag=0
		dbpool=ht.tconnectdb(self.filename)
		wfd = defer.waitForDeferred(ht.tupdateflag(self,dbpool,guid,flag))
		yield wfd
		ht.tclosedb(dbpool)
		return

	def closestpeer(self, peerid, peerlist):
		# Given a peerid, it finds the closest in distance to peerid from a list of other peerid
		# This is used to find a particular peer.  It will search the the routing table for the 
		# closest peer and if not found it will search the closest peer routing table for the 
		# peer and so forth until it finds the correct peer
		closestdistance=999999999999999999999999999999999999999999
		closestpeer=peerid
		for peer in peerlist:
			#print "peer = "+str(peer)
			d1=self.getdistance(peerid,peer)
			#print "d1 = "+str(d1)
			if (d1<closestdistance):
				closestdistance=d1
				closestpeer=peer
				#print "cd = "+str(closestdistance)
				#print "cp = "+str(peer)
		#print "closest distance is "+str(closestdistance)
		return closestpeer,d1

	def farestpeer(self,peerid, peerlist):
		# Will determine the farthest peer in a given peer hash table.
		farestdistance=0
		farestpeer=peerid
		for peer in peerlist:
			#print "peer = "+str(peer)
			d1=self.getdistance(peerid,peer)
			#print "d1 = "+str(d1)
			if (d1>farestdistance):
				farestdistance=d1
				farestpeer=peer
				#print "cd = "+str(closestdistance)
				#print "cp = "+str(peer)
		#print "farest distance is "+str(farestdistance)
		return farestpeer,d1

	def gettimestamp(self):
		# Ts course timestamp
		time1=time.time()
		return time1

	def getwebpage(self,url):
		d = getPage(url)
		d.addCallback(self.getwebpage_callback)
		return d
    
	def getwebpage_callback(self,html):
		h=str(html)
	        print "html - ",h
		return h

	@defer.deferredGenerator
	def postipaddress(self,address):
		ipaddress = address+"?guid="+str(self.guid)+"&address="+str(self.address)+"&=port"+str(self.port)
		wfd = defer.waitForDeferred(self.getwebpage(ipaddress))
		yield wfd
		pageresult = wfd.getResult()
		return

	@defer.deferredGenerator
	def getipaddress(self):
		pageresult="0"
		wfd = defer.waitForDeferred(self.getwebpage("http://91.198.22.70/"))
		yield wfd
		pageresult = wfd.getResult()
		if (pageresult !="0"):
			int1=pageresult.find("Address:")+9
			str1=pageresult[int1:]
			int2=str1.find("<")
			str2=str1[:int2]
			print "ipaddress - ",str2
		else:
			wfd = defer.waitForDeferred(self.getwebpage("http://www.myipaddress.com/"))
			yield wfd
			pageresult = wfd.getResult()
			if (pageresult !="0"): 
				int1=pageresult.find("Your computer's IP address is:")+60
				str1=pageresult[int1:]
				int2=str1.find("<")
				str2=str1[:int2]
				print "ipaddress - ",str2
			else:
				wfd = defer.waitForDeferred(self.getwebpage("http://ipinfo.info/index.php"))
				yield wfd
				pageresult = wfd.getResult()
				if (pageresult !="0"):
					int1=pageresult.find("My public IP Address:")+266
					str1=pageresult[int1:]
					int2=str1.find("<")
					str2=str1[:int2]
					print "ipaddress - ",str2
				else:
					print "[error] - internet connection seems to be down" 
		return
		

class encyption:

	KEY_LENGTH = 1024

	def blank_callback():
    		print "Replace the default dashes"
    		return

	def generatewalletkeys(self,fname):
		privpem=fname+"-private.pem"
		pubpem=fname+"-public.pem"
		# Random seed
		Rand.rand_seed (os.urandom (self.KEY_LENGTH))
		# Generate key pair
		key = RSA.gen_key (self.KEY_LENGTH, 65537)
		#Save private key
		key.save_key (privpem, None)
		#Save public key
		key.save_pub_key (pubpem)
		print "Wallet keys has been generated"
		return

	def generatekeys(self):
		# Random seed
		Rand.rand_seed (os.urandom (self.KEY_LENGTH))
		# Generate key pair
		key = RSA.gen_key (self.KEY_LENGTH, 65537)
		# Create memory buffers
		pri_mem = BIO.MemoryBuffer()
		pub_mem = BIO.MemoryBuffer()
		# Save keys to buffers
		key.save_key_bio(pri_mem, None)
		key.save_pub_key_bio(pub_mem)
		# Get keys 
		public_key = pub_mem.getvalue()
		private_key = pri_mem.getvalue()
		return public_key, private_key

	def getpublickey(self,fname):
		pubpem=fname+"-public.pem"
		pubkey = RSA.load_pub_key (pubpem)
		pub_mem = BIO.MemoryBuffer()
		pubkey.save_pub_key_bio(pub_mem)
		public_key = pub_mem.getvalue()
		print "public_key=",public_key
		return public_key

	def getpubkey(self,fname):
		pubpem=fname+"-public.pem"
		pubkey = RSA.load_pub_key (pubpem)
		return pubkey

	def getprivatekey(self,fname):
		privpem=fname+"-private.pem"
		prikey = RSA.load_key (privpem)
		return prikey

	def encyptmessage(self,message,pubkey):
		#encrypt the message using that public key
		#Only the private key can decrypt a message encrypted using the public key
		CipherText = pubkey.public_encrypt (message, RSA.pkcs1_oaep_padding)
		#print CipherText.encode ('base64')
		print "CipherText - ",CipherText.encode ('base64')
		return CipherText.encode ('base64')

	def signmessage(self,CipherText,prikey):
		# Generate a signature
		#MsgDigest = M2Crypto.EVP.MessageDigest ('sha1')
		MsgDigest = EVP.MessageDigest ('sha1')
		MsgDigest.update (CipherText)
		Signature = prikey.sign_rsassa_pss (MsgDigest.digest ())
		#print Signature.encode ('base64')
		return Signature

	def verifymessage(self,CipherText,Signature,fname):
		pubpem=fname+"-public.pem"
		# Load the public key
  		VerifyRSA = M2Crypto.RSA.load_pub_key (pubpem)
  		# Verify the signature
		MsgDigest = M2Crypto.EVP.MessageDigest ('sha1')
  		MsgDigest.update (CipherText)
		if VerifyRSA.verify_rsassa_pss (MsgDigest.digest (), Signature) == 1:
			print "This message was sent by Alice.\n"
			verify = True
		else:
			print "This message was NOT sent by Alice!\n"
			verify = False
		return verify

	def decyptmessage(self,CipherText,fname):
		privpem=fname+"-private.pem"
		# load the private key
		ReadRSA = M2Crypto.RSA.load_key (privpem)
		# decrypt the message using that private key
		# If you use the wrong private key to try to decrypt the message it generates an exception
		try:
  			PlainText = ReadRSA.private_decrypt (CipherText, M2Crypto.RSA.pkcs1_oaep_padding)
		except:
  			print "Error: wrong key?"
  			PlainText = ""

		if PlainText!="":
  			# print the result of the decryption
  			print "Message decrypted by Bob:"
  			print PlainText
		return PlainText

	def signastring(self,message,fname):
		privpem=fname+"-private.pem"
		#Generate a signature for a string
		#Use the private key
		SignEVP = M2Crypto.EVP.load_key (privpem)
		#Begin signing
		SignEVP.sign_init ()
		#Tell it to sign our string
		SignEVP.sign_update (message)
		#Get the final result
		StringSignature = SignEVP.sign_final ()
		#Print the final result
		print "Bob's signature for the string:"
		print StringSignature.encode ('base64')
		return StringSignature

	def verifyastring(self,StringSignature,message,fname):
		pubpem=fname+"-public.pem"
		#Verify the string was signed by the right person 
		PubKey = M2Crypto.RSA.load_pub_key (pubpem)
		#Initialize
		VerifyEVP = M2Crypto.EVP.PKey()
		#Assign the public key to our VerifyEVP
		VerifyEVP.assign_rsa (PubKey)
		#Begin verification
		VerifyEVP.verify_init ()
		#Tell it to verify our string, if this string is not identicial to the one that was signed, it will fail
		VerifyEVP.verify_update (message)
		#Was the string signed by the right person?
		if VerifyEVP.verify_final (StringSignature) == 1:
 			print "The string was successfully verified."
			verify = True
		else:
 			print "The string was NOT verified!"
			verify = False
		return verify

class logfile:

	def openlogw(self):
		fo = open("./test/log.txt", "a")
		return fo

	def openlogr(self):
		fo = open("./test/log.txt", "r")
		return fo

	def readlogline(self,fo):
		line = fo.readline()
		return line

	def writelog(self,fo,str1):
		localtime = time.asctime( time.localtime(time.time()) )
		fo.write(str(localtime)+"     "+str1+"\n");
		return

	def closelog(self,fo):
		fo.close()
		return

	def printinfo(self,str1):
		fo=self.openlogw()
		self.writelog(fo,str1)
		self.closelog(fo)
		return

def main():
	global FNAME,ADDRESS,PORT
	print "Testing the zeitcoin utility classes...."
	ut=utility(FNAME,ADDRESS,PORT)
	en=encyption()
	guid=ut.generateguid()
	print "guid - ",guid
	pubkey,privkey=en.generatekeys()
	print "public key - ",pubkey
	print "private key - ",privkey
	print "Getting webpage http://91.198.22.70/ "
	#ut.getwebpage("http://91.198.22.70/")
	ut.getipaddress()
	print "Finish testing the zeitcoin utility classes"
	reactor.run()
	sys.exit(0)
	 
if __name__ == "__main__" : main()
