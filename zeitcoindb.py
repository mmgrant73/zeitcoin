#!/usr/bin/env python
#########################################
# Zeitcoin Database Class
#########################################

import sqlite3, sys
from twisted.enterprise import adbapi
from twisted.internet import reactor, defer

class hashtable:

	def tconnectdb(self,fname):
		db=fname+".db"
		dbpool = adbapi.ConnectionPool("sqlite3" , db,  check_same_thread=False)
		return dbpool

	def connectdb(self,fname):
		db=fname+".db"
		conn = sqlite3.connect(db)
		c = conn.cursor()
		#print "zeitcoin database has been open"
		return conn, c

	def createwallet(self,conn,c):
		# Create table
		c.execute('''CREATE TABLE wallet (guid text, balance integer, time real)''')
		conn.commit()
		print "wallet table has been created"
		return

	def createht(self,conn,c):
		# Create table
		c.execute('''CREATE TABLE hashtable (guid text, address text, port integer, flag integer, time real)''')
		conn.commit()
		print "hash table has been created"
		return

	def createtb(self,conn,c):
		# Create transaction block table that holds: transaction id, transaction hash, timestamp
		c.execute('''CREATE TABLE blocktrans (txid text, thash text, time real)''')
		conn.commit()
		print "transaction table table has been created"
		return

	def createlt(self,conn,c):
		# Create local transaction list that holds: txid, thash, addresswallet,addressother, amount, timestamp
		c.execute('''CREATE TABLE localtrans (txid text, thash text, addresswallet text, addressother text, amount integer, type text, time real)''')
		conn.commit()
		print "local transaction table has been created"
		return

	def createaccount(self,conn,c):
		# Create the account table that holds: address, privkey, pubkey and account name
		c.execute('''CREATE TABLE accounts (address text, privkey text, pubkey text, account text, time real)''')
		conn.commit()
		print "the account table has been created"
		return

	def createleader(self,conn,c):
		# Create the leader table that holds: sharedkeys, address, port, guid, timestamp
		c.execute('''CREATE TABLE leader (sharedkeys text, address text, port integer, guid text, time real)''')
		conn.commit()
		print "leader table has been created"
		return

	def addaccount(self,conn,c,account,privkey,pubkey,address,time1):
		# add a new account
		c.execute("INSERT INTO accounts VALUES ('"+str(address)+"','"+str(privkey)+"','"+str(pubkey)+"','"+str(account)+"','"+str(time1)+"')")
		conn.commit()
		print "data added to the account table"
		return

	def _taddaccount(self,txn,account,privkey,pubkey,address,time1):
		# add a new account
		txn.execute("INSERT INTO accounts VALUES ('"+str(address)+"','"+str(privkey)+"','"+str(pubkey)+"','"+str(account)+"','"+str(time1)+"')")
		#conn.commit()
		print "data added to the account table"
		return

	def taddaccount(self,dbpool,account,privkey,pubkey,address,time1):
    		return dbpool.runInteraction(self._taddaccount,account,privkey,pubkey,address,time1)

	def addwallet(self,conn,c,guid,balance,time1):
		# add a new account
		c.execute("INSERT INTO wallet VALUES ('"+str(guid)+"','"+str(balance)+"','"+str(time1)+"')")
		conn.commit()
		print "data added to the wallet table"
		return

	def addtb(self,conn,c,txid,thash,time1):
		# add a new transaction to the block transaction id, transaction hash, timestamp
		c.execute("INSERT INTO blocktrans VALUES ('"+str(txid)+"','"+str(thash)+"','"+str(time1)+"')")
		conn.commit()
		print "data added to the transaction block table"
		return

	def _taddtb(self,txn,txid,thash,time1):
		# add a new transaction to the block transaction id, transaction hash, timestamp
		txn.execute("INSERT INTO blocktrans VALUES ('"+str(txid)+"','"+str(thash)+"','"+str(time1)+"')")
		#conn.commit()
		print "data added to the transaction block table"
		return

	def taddtb(self,dbpool,txid,thash,time1):
    		return dbpool.runInteraction(self._taddtb,txid,thash,time1)

	def addlt(self,conn,c,txid,thash,addresswallet,addressother,amount,type1,time1):
		# add a new transaction to the local list txid, thash, addresswallet,addressother, amount, timestamp
		c.execute("INSERT INTO localtrans VALUES ('"+str(txid)+"','"+str(thash)+"','"+str(addresswallet)+"','"+str(addressother)+"',"+str(amount)+",'"+str(type1)+"','"+str(time1)+"')")
		conn.commit()
		print "data added to the local transaction table"
		return

	def _taddlt(self,txn,txid,thash,addresswallet,addressother,amount,type1,time1):
		# add a new transaction to the local list txid, thash, addresswallet,addressother, amount, timestamp
		txn.execute("INSERT INTO localtrans VALUES ('"+str(txid)+"','"+str(thash)+"','"+str(addresswallet)+"','"+str(addressother)+"',"+str(amount)+",'"+str(type1)+"','"+str(time1)+"')")
		#conn.commit()
		print "data added to the local transaction table"
		return

	def taddlt(self,dbpool,txid,thash,addresswallet,addressother,amount,type1,time1):
    		return dbpool.runInteraction(self._taddlt,txid,thash,addresswallet,addressother,amount,type1,time1)


	def addht(self,conn,c,guid,address,port,flag,time1):
		# Insert a row of data
		c.execute("INSERT INTO hashtable VALUES ('"+guid+"','"+address+"',"+str(port)+","+str(flag)+","+str(time1)+")")
		conn.commit()
		print "data added to the hashtable"
		return

	def _taddht(self,txn,guid,address,port,flag,time1):
		# Insert a row of data
		txn.execute("INSERT INTO hashtable VALUES ('"+guid+"','"+address+"',"+str(port)+","+str(flag)+","+str(time1)+")")
		#conn.commit()
		print "data added to the hashtable"
		return

	def taddht(self,dbpool,guid,address,port,flag,time1):
    		return dbpool.runInteraction(self._taddht,guid,address,port,flag,time1)

	def addleader(self,conn,c,sharedkey, address, port, guid, timestamp):
		# adds to the leader table  sharedkeys, address, port, guid, timestamp
		c.execute("INSERT INTO leader VALUES ('"+str(sharedkey)+"','"+str(address)+"',"+str(port)+",'"+str(guid)+"',"+str(timestamp)+")")
		conn.commit()
		print "data added to the leader table"
		return

	def _taddleader(self,txn,sharedkey, address, port, guid, timestamp):
		# adds to the leader table  sharedkeys, address, port, guid, timestamp
		txn.execute("INSERT INTO leader VALUES ('"+str(sharedkey)+"','"+str(address)+"',"+str(port)+",'"+str(guid)+"',"+str(timestamp)+")")
		#conn.commit()
		print "data added to the leader table"
		return

	def taddleader(self,dbpool,sharedkey, address, port, guid, timestamp):
    		return dbpool.runInteraction(self._taddleader,sharedkey, address, port, guid, timestamp)

	def deleteht(self,conn,c,guid):
		# Delete a row of data
		c.execute("DELETE from hashtable where guid='"+guid+"'")
		conn.commit()
		print "data was delete from the hashtable"
		return

	def _tdeleteht(self,txn,guid):
		# Delete a row of data
		txn.execute("DELETE from hashtable where guid='"+guid+"'")
		#conn.commit()
		print "data was delete from the hashtable"
		return

	def tdeleteht(self,dbpool,guid):
    		return dbpool.runInteraction(self._tdeleteht,guid)

	def deleteleader(self,conn,c):
		# Delete all from the leader table
		c.execute("DELETE from leader")
		conn.commit()
		print "all data was delete from the leader table"
		return

	def tdeleteleader(self,txn):
		# Delete all from the leader table
		txn.execute("DELETE from leader")
		#conn.commit()
		print "all data was delete from the leader table"
		return

	def tdeleteleader(self,dbpool):
    		return dbpool.runInteraction(self._tdeleteleader)

	def deleteallht(self,conn,c):
		# Delete all from the leader table
		c.execute("DELETE from hashtable")
		conn.commit()
		print "all data was delete from the hash table"
		return

	def deleteallwallet(conn,c):
		# Delete all from the leader table
		c.execute("DELETE from wallet")
		conn.commit()
		print "all data was delete from the wallet table"
		return

	def deleteallblocktrans(self,conn,c):
		# Delete all from the leader table
		c.execute("DELETE from blocktrans")
		conn.commit()
		print "all data was delete from the blocktrans table"
		return

	def deletealllocaltrans(self,conn,c):
		# Delete all from the leader table
		c.execute("DELETE from localtrans")
		conn.commit()
		print "all data was delete from the localtrans table"
		return

	def deleteallaccounts(self,conn,c):
		# Delete all from the leader table
		c.execute("DELETE from accounts")
		conn.commit()
		print "all data was delete from the accounts table"
		return

	def deleteleaderrow(self,con,c, guid):
		# Delete a row from the leader table
		c.execute("DELETE from leader where guid='"+guid+"'")
		conn.commit()
		print "data was delete from the leader table"
		return

	def getalltb(self,c):
		# Get all transaction from the block
		tblist=[]
		for row in c.execute('SELECT * FROM blocktrans order by time'):
			tblist.append(row)
        		#print row
		return tblist

	def _tgetalltb(self,txn):
		# Get all transaction from the block
		tblist=[]
		for row in txn.execute('SELECT * FROM blocktrans order by time'):
			tblist.append(row)
        		#print row
		return tblist

	def tgetalltb(self,dbpool):
    		return dbpool.runInteraction(self._tgetalltb)

	def getalllt(self,c):
		# Get all local transaction
		peerlist=[]
		for row in c.execute('SELECT * FROM localtrans'):
			peerlist.append(row)
        		#print row
		return peerlist

	def _tgetalllt(self,txn):
		# Get all local transaction
		peerlist=[]
		for row in txn.execute('SELECT * FROM localtrans'):
			peerlist.append(row)
        		#print row
		return peerlist

	def tgetalllt(self,dbpool):
    		return dbpool.runInteraction(self._tgetalllt)

	def _tgetallwallet(self,txn):
		# Get all local transaction
		peerlist=[]
		for row in txn.execute('SELECT * FROM wallet'):
			peerlist.append(row)
        		print row
		return peerlist

	def tgetallwallet(self,dbpool):
    		return dbpool.runInteraction(self._tgetallwallet)

	def getallwallet(self,c):
		# Get all local transaction
		peerlist=[]
		for row in c.execute('SELECT * FROM wallet'):
			peerlist.append(row)
        		#print row
		return peerlist

	def getallleader(self,c):
		# Get all local transaction
		peerlist=[]
		for row in c.execute('SELECT * FROM leader'):
			peerlist.append(row)
        		#print row
		return peerlist

	def _tgetallleader(self,txn):
		# Get all local transaction
		peerlist=[]
		for row in txn.execute('SELECT * FROM leader'):
			peerlist.append(row)
        		#print row
		return peerlist

	def tgetallleader(self,dbpool):
    		return dbpool.runInteraction(self._tgetallleader)

	def getlisttrans(self,c,starttrans,length):
		# Get all local transaction
		translist=[]
		count1=0
		for row in c.execute('SELECT * FROM localtrans order by time'):
			if (count1>=starttrans and count1<=starttrans+length):
				translist.append(row)
        			print row
			count1=count1+1
		return translist

	def _tgetlisttrans(self,txn,starttrans,length):
		# Get all local transaction
		translist=[]
		count1=0
		for row in txn.execute('SELECT * FROM localtrans order by time'):
			if (count1>=starttrans and count1<=starttrans+length):
				translist.append(row)
        			print row
			count1=count1+1
		return translist

	def tgetlisttrans(self,starttrans,length,dbpool):
    		return dbpool.runInteraction(self._tgetlisttrans,starttrans,length)

	def getlistaccounttrans(self,c,account):
		# Get all local transaction
		translist=[]
		count1=0
		for row in c.execute("SELECT * FROM localtrans where account='"+account+"'order by timestamp"):
			translist.append(row)
        		print row
			count1=count1+1
		return translist

	def _tgetlistaccounttrans(self,txn,account):
		# Get all local transaction
		translist=[]
		count1=0
		for row in txn.execute("SELECT * FROM localtrans where account='"+account+"'order by timestamp"):
			translist.append(row)
        		print row
			count1=count1+1
		return translist

	def tgetlistaccounttrans(self,account,dbpool):
    		return dbpool.runInteraction(self._tgetlistaccounttrans,account)

	def getaddresstrans(self,c,address):
		# Get all local transaction
		translist=[]
		count1=0
		c.execute("SELECT * FROM localtrans where addresswallet='"+address+"'")
		res=c.fetchone()
		return res

	def _tgetaddresstrans(self,txn,address):
		# Get all local transaction
		translist=[]
		count1=0
		txn.execute("SELECT * FROM localtrans where addresswallet='"+address+"'")
		res=txn.fetchone()
		return res

	def tgetaddresstrans(self,address,dbpool):
    		return dbpool.runInteraction(self._tgetaddresstrans,address)

	def getallaccount(self,c):
		# Get all account:
		accountlist=[]
		for row in c.execute('SELECT * FROM accounts'):
			accountlist.append(row)
        		#print row
		return accountlist

	def _tgetallaccount(self,txn):
		# Get all account:
		accountlist=[]
		for row in txn.execute('SELECT * FROM accounts'):
			accountlist.append(row)
        		#print row
		return accountlist

	def tgetallaccount(self,dbpool):
    		return dbpool.runInteraction(self._tgetallaccount)

	def getaddresses(self,c,account):
		# Get all account:
		addresslist=[]
		for row in c.execute("SELECT address FROM accounts where account='"+account+"'"):
			addresslist.append(row[0])
        		print row
		return addresslist

	def _tgetaddresses(self,txn,account):
		# Get all account:
		addresslist=[]
		for row in txn.execute("SELECT address FROM accounts where account='"+account+"'"):
			addresslist.append(row[0])
        		print row
		return addresslist

	def tgetaddress(self,account,dbpool):
    		return dbpool.runInteraction(self._tgetaddress,account)

	def getallht(self,c):
		peerlist=[]
		for row in c.execute('SELECT * FROM hashtable'):
			peerlist.append(row)
        		#print row
		return peerlist

	def _tgetallht(self,txn):
		peerlist=[]
		for row in txn.execute('SELECT * FROM hashtable'):
			peerlist.append(row)
        		#print row
		return peerlist

	def tgetallht(self,dbpool):
    		return dbpool.runInteraction(self._tgetallht)

	def getallguidht(self,c):
		peerlist=[]
		for row in c.execute('SELECT guid FROM hashtable'):
			peerlist.append(row[0])
        		#print row
		return peerlist

	def _tgetallguidht(self,txn):
		peerlist=[]
		for row in txn.execute('SELECT guid FROM hashtable'):
			peerlist.append(row[0])
        		#print row
		return peerlist

	def tgetallguidht(self,dbpool):
    		return dbpool.runInteraction(self._tgetallguidht)

	def getlineht(self,c,guid):
		c.execute("SELECT * FROM hashtable WHERE guid='"+guid+"'")
		res=c.fetchone()
		return res

	def getaddress(self,c,guid):
		c.execute("SELECT address,port FROM hashtable WHERE guid='"+guid+"'")
		res=c.fetchone()
		address=res[0]
		port=res[1]
		return address,port

	def _tgetaddress(self,txn,guid,d1):
		txn.execute("SELECT address,port FROM hashtable WHERE guid='"+guid+"'")
		res=txn.fetchone()
		address=res[0]
		port=res[1]
		return address,port,guid,d1

	def tgetaddress(self,dbpool,guid,d1):
		print "guid  = ",guid
		print "dbpool = ",dbpool
    		return dbpool.runInteraction(self._tgetaddress,guid,d1)

	def getbalance(self,c,guid):
		c.execute("SELECT balance FROM wallet WHERE guid='"+guid+"'")
		res=c.fetchone()
		balance=res[0]
		return balance

	def _tgetbalance(self,txn,guid):
		#print "guid-",guid
		txn.execute("SELECT balance FROM wallet WHERE guid='"+guid+"'")
		res=txn.fetchone()
		balance=res[0]
		return balance

	def tgetbalance(self,guid,dbpool):
		#print "guid,  = ",guid
    		return dbpool.runInteraction(self._tgetbalance,guid)

	def getnewbalance(self,c,guid):
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='received'")
		res=c.fetchone()
		received=res[0]
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='sent'")
		res=c.fetchone()
		sent=res[0]
		return received-sent

	def _tgetnewbalance(self,txn):
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='received'")
		res=c.fetchone()
		received=res[0]
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='sent'")
		res=c.fetchone()
		sent=res[0]
		return int(received)-int(sent)

	def tgetnewbalance(self,dbpool):
		#print "guid,  = ",guid
    		return dbpool.runInteraction(self._tgetnewbalance,guid)

	def getaccountbalance(self,c,account):
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='received' and account='"+account+"'")
		res=c.fetchone()
		received=res[0]
		c.execute("SELECT sum(amount) FROM localtrans WHERE type='sent'and account='"+account+"'")
		res=c.fetchone()
		sent=res[0]
		return received-sent

	def _tgetaccountbalance(self,txn,account):
		txn.execute("SELECT sum(amount) FROM localtrans WHERE type='received' and account='"+account+"'")
		res=txn.fetchone()
		received=res[0]
		txn.execute("SELECT sum(amount) FROM localtrans WHERE type='sent'and account='"+account+"'")
		res=txn.fetchone()
		sent=res[0]
		return received-sent

	def tgetaccountbalance(self,account,dbpool):
    		return dbpool.runInteraction(self._tgetaccountbalance,account)

	def getguid(self,c):
		c.execute("SELECT guid FROM wallet")
		res=c.fetchone()
		guid=res[0]
		return guid

	def _tgetguid(self,txn):
		txn.execute("SELECT guid FROM wallet")
		res=txn.fetchone()
		guid=res[0]
		print "getguid=",guid
		return guid

	def tgetguid(self,dbpool):
    		return dbpool.runInteraction(self._tgetguid)

	def gettb(self,c,thash):
		# Get a transaction from the block
		c.execute("SELECT * FROM blocktrans WHERE thash='"+thash+"'")
		res=c.fetchone()
		txid=res[0]
		thash=res[1]
		time1=res[2]
		return txid,thash,time1

	def _tgettb(self,txn,thash):
		# Get a transaction from the block
		txn.execute("SELECT * FROM blocktrans WHERE thash='"+thash+"'")
		res=txn.fetchone()
		txid=res[0]
		thash=res[1]
		time1=res[2]
		return txid,thash,time1

	def tgettb(self,thash,dbpool):
    		return dbpool.runInteraction(self._tgettb,thash)

	def getlt(self,c,txid):
		# Get a txid from the local transaction list
		c.execute("SELECT * FROM localtrans WHERE txid='"+txid+"'")
		# add a check in case of nothing return
		res=c.fetchone()
		txid=res[0]
		thash=res[1]
		addresswallet=res[2]
		addressother=res[3]
		amount=res[4]
		time1=res[5]
		return txid,thash,addresswallet,addressother,time1

	def _tgetlt(self,txn,txid):
		# Get a txid from the local transaction list
		txn.execute("SELECT * FROM localtrans WHERE txid='"+txid+"'")
		# add a check in case of nothing return
		res=txn.fetchone()
		txid=res[0]
		thash=res[1]
		addresswallet=res[2]
		addressother=res[3]
		amount=res[4]
		time1=res[5]
		return txid,thash,addresswallet,addressother,time1

	def tgetlt(self,thash,dbpool):
    		return dbpool.runInteraction(self._tgetlt,thash)

	def getaccount(self,c,address):
		# Get an account address text, privkey text, pubkey text, account text, time real
		c.execute("SELECT * FROM accounts WHERE address='"+address+"'")
		# add a check in case of nothing return
		res=c.fetchone()
		address=res[0]
		privkey=res[1]
		pubkey=res[2]
		account=res[3]
		time1=res[4]
		return address,privkey,pubkey,account,time1

	def _tgetaccount(self,txn,address):
		# Get an account address text, privkey text, pubkey text, account text, time real
		txn.execute("SELECT * FROM accounts WHERE address='"+address+"'")
		# add a check in case of nothing return
		res=txn.fetchone()
		address=res[0]
		privkey=res[1]
		pubkey=res[2]
		account=res[3]
		time1=res[4]
		return address,privkey,pubkey,account,time1

	def tgetaccount(self,address,dbpool):
    		return dbpool.runInteraction(self._tgetaccount,address)

	def getleader(self,guid):
		# Get a row from the leader table based on guid
		c.execute("SELECT sharedkey, address, port, guid, time FROM leader WHERE guid='"+guid+"'")
		# add a check in case of nothing return
		res=c.fetchone()
		address=res[0]
		port=res[1]
		return

	def _tgetleader(self,txn,guid):
		# Get a row from the leader table based on guid
		txn.execute("SELECT sharedkey, address, port, guid, time FROM leader WHERE guid='"+guid+"'")
		# add a check in case of nothing return
		res=txn.fetchone()
		address=res[0]
		port=res[1]
		return

	def tgetleader(self,guid,dbpool):
    		return dbpool.runInteraction(self._tgetleader,guid)

	def getkeys(self,guid):
		# Get a row from the leader table based on guid
		keylist=[]
		for row in c.execute('SELECT sharedkey FROM leader'):
			keylist.append(row[0])
        		print row
		return keylist

	def _tgetkeys(self,guid):
		# Get a row from the leader table based on guid
		keylist=[]
		for row in txn.execute('SELECT sharedkey FROM leader'):
			keylist.append(row[0])
        		print row
		return keylist

	def tgetkeys(self,guid,dbpool):
    		return dbpool.runInteraction(self._tgetkeys,guid)

	def updatetime(self,conn,c,guid):
		time1=time.time() #taddht(self,dbpool,guid,address,port,flag,time1)
		c.execute("UPDATE hashtable SET time = "+str(time1)+" where guid='"+guid+"'")
		conn.commit()
		print "time was updated in the hashtable"
		return

	def _tupdatetime(self,txn,guid):
		time1=time.time()
		txn.execute("UPDATE hashtable SET time = "+str(time1)+" where guid='"+guid+"'")
		#conn.commit()
		print "time was updated in the hashtable"
		return

	def tupdatetime(self,dbpool,guid):
    		return dbpool.runInteraction(self._tupdatetime,guid)

	def _tupdatepeer(self,txn,guid,address,port):
		time1=time.time()
		txn.execute("UPDATE hashtable SET address = "+str(address)+", port = "+str(port)+",flag = 0 ,time = "+str(time1)+" where guid='"+guid+"'")
		#conn.commit()
		print "peer was updated in the hashtable"
		return

	def tupdatepeer(self,dbpool,guid,address,port):
    		return dbpool.runInteraction(self._tupdatepeer,guid,address,port)

	def updatebalance(self,conn,c,guid):
		balance=self.getnewbalance(c,guid)
		c.execute("UPDATE hashtable SET balance = "+str(balance)+" where guid='"+guid+"'")
		conn.commit()
		print "balance was updated in the wallet table"
		return

	def _tupdatebalance(self,txn,balance,guid):
		#balance=self.getnewbalance(c,guid)
		txn.execute("UPDATE hashtable SET balance = "+str(balance)+" where guid='"+guid+"'")
		conn.commit()
		print "balance was updated in the wallet table"
		return

	def tupdatebalance(self,dbpool,balance,guid):
    		return dbpool.runInteraction(self._tupdatebalance,guid)

	def updateflag(self,conn,c,guid,flag):
		c.execute("UPDATE hashtable SET flag = "+str(flag)+" where guid='"+guid+"'")
		conn.commit()
		print "flag was updated in the hashtable"
		return

	def _tupdateflag(self,txn,guid,flag):
		txn.execute("UPDATE hashtable SET flag = "+str(flag)+" where guid='"+guid+"'")
		#conn.commit()
		print "flag was updated in the hashtable"
		return

	def tupdateflag(self,dbpool,guid,flag):
    		return dbpool.runInteraction(self._tupdateflag,guid,flag)

	def numht(self,c):
		c.execute('SELECT count(*) FROM hashtable')
		res=c.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable"
		return count1

	def _tnumht(self,txn):
		txn.execute('SELECT count(*) FROM hashtable')
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable"
		return count1

	def tnumht(self,dbpool):
    		return dbpool.runInteraction(self._tnumht)

	def numtb(self,c):
		c.execute('SELECT count(*) FROM blocktrans')
		res=c.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the blocktrans table"
		return count1


	def _tnumtb(self,txn):
		txn.execute('SELECT count(*) FROM blocktrans')
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the blocktrans table"
		return count1

	def tnumtb(self,dbpool):
    		return dbpool.runInteraction(self._tnumtb)

	def numtg(self,c):
		c.execute('SELECT count(*) FROM leader')
		res=c.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the leader table"
		return count1

	def _tnumtg(self,txn):
		txn.execute('SELECT count(*) FROM leader')
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the leader table"
		return count1

	def tnumtg(self,dbpool):
    		return dbpool.runInteraction(self._tnumtg)

	def checkfullht(self,conn,c):
		# Check to see if hash table is full (more than 127 rows)
		full=False
		self.numht(c)
		if (count1>127):
			full=True
		return full

	def _tcheckfullht(self,txn):
		# Check to see if hash table is full (more than 127 rows)
		full=False
		#self.numht(c)
		txn.execute('SELECT count(*) FROM hashtable')
		res=txn.fetchone()
		count1=int(res[0])
		if (count1>127):
			full=True
		return full

	def tcheckfullht(self,dbpool):
    		return dbpool.runInteraction(self._tcheckfullht)

	def checkguid(self,conn,c,guid):
		# Check to see if a guid is in the hash table
		guidexist=False
		c.execute("SELECT count(*) FROM hashtable where guid='"+guid+"'")
		res=c.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable with that guid"
		if (count1>0):
			guidexist=True
		return guidexist

	def _tcheckguid(self,txn,guid):
		# Check to see if a guid is in the hash table
		guidexist=False
		txn.execute("SELECT count(*) FROM hashtable where guid='"+guid+"'")
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable with that guid"
		if (count1>0):
			guidexist=True
		return guidexist

	def tcheckguid(self,dbpool,guid):
    		return dbpool.runInteraction(self._tcheckguid,guid)

	def _tcheckpeer(self,txn,guid,address,port):
		# Check to see if a guid is in the hash table
		guidexist=False
		txn.execute("SELECT count(*) FROM hashtable where guid='"+str(guid)+"' and address='"+str(address)+"' and port'"+str(port)+"'")
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable with that guid, address and port"
		if (count1>0):
			guidexist=True
		return guidexist

	def tcheckpeer(self,dbpool,guid,address,port):
    		return dbpool.runInteraction(self._tcheckpeer)

	def _tgetflag(self,txn,guid):
		# Check to see if a guid is in the hash table
		guid=0
		txn.execute("SELECT guid FROM hashtable where flag=0 orderby timestamp")
		res=txn.fetchone()
		guid=int(res[0])
		print "There is an inactive flag"
		return guid

	def tgetflag(self,dbpool):
    		return dbpool.runInteraction(self._tgetflag)

	def checktrans(self,conn,c,txid):
		# Check to see if a guid is in the hash table
		txidexist=False
		c.execute("SELECT count(*) FROM blocktrans where txid='"+str(txid)+"'")
		res=c.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable with that guid"
		if (count1>0):
			txidexist=True
		return txidexist

	def _tchecktrans(self,txn,txid):
		# Check to see if a guid is in the hash table
		txidexist=False
		txn.execute("SELECT count(*) FROM blocktrans where txid='"+str(txid)+"'")
		res=txn.fetchone()
		count1=int(res[0])
		print "There are "+str(count1)+" rows in the hashtable with that guid"
		if (count1>0):
			txidexist=True
		return txidexist

	def tchecktrans(self,txid,dbpool):
    		return dbpool.runInteraction(self._tchecktrans,txid)

	def closedb(self,conn):
		conn.close()
		#print "zeitcoin database has been closed"
		return

	def tclosedb(self,dbpool):
		dbpool.close()
		#print "zeitcoin database has been closed"
		return

@defer.deferredGenerator
def showhashdb():
	print "=============Hash table Twisted=================="
	ht=hashtable()
	dbpool=ht.tconnectdb('zeitcoin')
	wfd = defer.waitForDeferred(ht.tgetallht(dbpool))
	yield wfd
	list1 = wfd.getResult()
	for i in list1:
		print i
	ht.tclosedb(dbpool)
	reactor.stop()
	return

def showhashdb1():
	print "=================Hash table======================="
	ht=hashtable()
	conn,c=ht.connectdb('zeitcoin')
	list1=ht.getallht(c)
	for i in list1:
		print i
	ht.closedb(conn)
	return
	

def main():
	print "Testing the zeitcoin database class...."
	print
	showhashdb1()
	print
	showhashdb()
	reactor.run()
	print
	print "Finish testing the zeitcoin database class"
	sys.exit(0)
	
  
if __name__ == "__main__" : main()
