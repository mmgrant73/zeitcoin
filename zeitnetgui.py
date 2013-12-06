#!/usr/bin/python
######################
# Zeitcoin Network GUI
######################


import wx.html as html
from wx import App
import wx
from twisted.internet import wxreactor
wxreactor.install()
import sys, os, uuid, time, threading, hashlib, shutil, sqlite3, random, subprocess
from M2Crypto import Rand, RSA, BIO
from twisted.web import server
from twisted.application import service, internet
from twisted.internet import reactor, defer, endpoints, task, threads
from twisted.internet.threads import deferToThread as __deferToThread
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
BALANCE=9
GUID=''

class zeitnet(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Zietcoin Wallet")

	self.panelhome = PanelHome(self)

	self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelhome, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

	self.shoption=fileMenu.Append(wx.ID_ANY, '&Option')
        self.shabout=fileMenu.Append(wx.ID_ANY, '&About')
        fileMenu.AppendSeparator()
        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Exit\tCtrl+W')
        fileMenu.AppendItem(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
	self.Bind(wx.EVT_MENU, self.OnAboutBox, self.shabout)
	self.Bind(wx.EVT_MENU, self.ShowOption,self.shoption)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.SetSize((800, 600))
        self.SetTitle('Zeitcoin Network')
        self.Centre()
        self.Show(True)

    def ShowOption(self, e):
	chgopt = ChangeOptions(None, title='Change Wallet Options')
        chgopt.ShowModal()
        chgopt.Destroy() 
	return
        
    def OnQuit(self, e):
	reactor.stop()
        self.Close()

    def OnAboutBox(self, e):
        
        description = """File Hunter is an advanced file manager for 
the Unix operating system. Features include powerful built-in editor, 
advanced search capabilities, powerful batch renaming, file comparison, 
extensive archive handling and more.
"""

        licence = """File Hunter is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

File Hunter is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""


        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon('./images/coin.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Zeitcoin Network')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) 2013 Matthew Grant')
        info.SetWebSite('http://www.zeitcoin.com')
        info.SetLicence(licence)
        info.AddDeveloper('Matthew Grant')
        info.AddDocWriter('Matthew Grant')
        info.AddArtist('The Zeitgeist Movement')
        info.AddTranslator('The Zeitgeist Movement')

        wx.AboutBox(info)


class PanelHome(wx.Panel):
 
   	def __init__(self, parent):
		global BALANCE
        	wx.Panel.__init__(self, parent=parent)

		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(10)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, label='Number of peers')
		st.SetFont(font)
		hbox.Add(st, flag=wx.RIGHT, border=10)
		self.tc = wx.TextCtrl(self,-1,'10')
		hbox.Add(self.tc, proportion=1, flag=wx.EXPAND)
		sta = wx.StaticText(self, label='Starting Port')
		sta.SetFont(font)
		hbox.Add(sta, flag=wx.RIGHT, border=10)
		self.tca = wx.TextCtrl(self,-1,'3000')
		hbox.Add(self.tca, proportion=1, flag=wx.EXPAND)
		startButton = wx.Button(self, label='Start')  
		stopButton = wx.Button(self, label='Stop')
		hbox.Add(startButton)
		hbox.Add(stopButton)

		vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, label='Commands')
		st1.SetFont(font)
		hbox1.Add(st1, flag=wx.RIGHT, border=200)
		st1a = wx.StaticText(self, label='Network Output')
		st1a.SetFont(font)
		hbox1.Add(st1a, flag=wx.RIGHT, border=200)
		st1b = wx.StaticText(self, label='Network Peers')
		st1b.SetFont(font)
		hbox1.Add(st1b, flag=wx.RIGHT, border=200)

		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		st11 = wx.StaticText(self, label='Commands')
		st11.SetFont(font)
		self.rb1 = wx.RadioButton(self, label='AMP Command',style=wx.RB_GROUP)
        	self.rb2 = wx.RadioButton(self, label='JSON-RPC Command')
        	self.rb3 = wx.RadioButton(self, label='Database Command')
		vbox2.Add(st11)
		vbox2.Add(self.rb1)
		vbox2.Add(self.rb2)
		vbox2.Add(self.rb3)

		vbox2.Add((-1, 10))

		st2b = wx.StaticText(self, label='Command to be sent')
		st2b.SetFont(font)
		vbox2.Add(st2b)

		com1 = ['ping','donetourguide','getguid','copyht','getclosest','getclosestpeer','sendpublickey','join','sendtotg','boardcasttrans', 'generatecoin','getnumtb','encryptdata','getleader','setleader','sendtransaction','gettransaction','getpuzzle','verifypuzzle','acceptcoin','updatetb','leave', 'leaderinfo' ,'initleader','getnewaddress']
        	self.cb2 = wx.ComboBox(self, choices=com1,style=wx.CB_READONLY)
		#self.st2 = wx.StaticText(self, label='')
		vbox2.Add(self.cb2)

		vbox2.Add((-1, 10))

		st2c = wx.StaticText(self, label='To Peer')
		st2c.SetFont(font)
		vbox2.Add(st2c)

		peers = ['1234','3000','3001','3002','3003','3004','3005','3006','3007','3008','3009','3010']
		self.cb2a = wx.ComboBox(self, choices=peers,style=wx.CB_READONLY)
		#self.st2 = wx.StaticText(self, label='')
		vbox2.Add(self.cb2a)

		vbox2.Add((-1, 10))

		self.st2d = wx.StaticText(self, label='Data1')
		self.st2d.SetFont(font)
		vbox2.Add(self.st2d)
		self.tc2d = wx.TextCtrl(self)
		vbox2.Add(self.tc2d, proportion=1, flag=wx.EXPAND)

		self.st2e = wx.StaticText(self, label='Data2')
		self.st2e.SetFont(font)
		vbox2.Add(self.st2e)
		self.tc2e = wx.TextCtrl(self)
		vbox2.Add(self.tc2e, proportion=1, flag=wx.EXPAND)

		self.st2f = wx.StaticText(self, label='Data3')
		self.st2f.SetFont(font)
		vbox2.Add(self.st2f)
		self.tc2f = wx.TextCtrl(self)
		vbox2.Add(self.tc2f, proportion=1, flag=wx.EXPAND)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		sendButton = wx.Button(self, label='Send')
		clearButton = wx.Button(self, label='Clear')
		hbox3.Add(sendButton)
		hbox3.Add(clearButton) 
		vbox2.Add(hbox3)		

		hbox2.Add(vbox2)

		self.tc2 = wx.TextCtrl(self, style=wx.TE_MULTILINE)

		redir=RedirectText(self.tc2)
		sys.stdout=redir
		#print "test"

		hbox2.Add(self.tc2, proportion=1, flag=wx.EXPAND)

		self.tc2a = wx.TextCtrl(self, style=wx.TE_MULTILINE)

		hbox2.Add(self.tc2a, proportion=1, flag=wx.EXPAND)

  		vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		startButton.Bind(wx.EVT_BUTTON, self.OnStart)
		stopButton.Bind(wx.EVT_BUTTON, self.OnStop)
		sendButton.Bind(wx.EVT_BUTTON, self.OnSend)
		clearButton.Bind(wx.EVT_BUTTON, self.OnClear)
		self.rb1.Bind(wx.EVT_RADIOBUTTON, self.Setamp)
        	self.rb2.Bind(wx.EVT_RADIOBUTTON, self.Setjsonrpc)
        	self.rb3.Bind(wx.EVT_RADIOBUTTON, self.Setdatabase)
		self.cb2.Bind(wx.EVT_COMBOBOX, self.OnSelect)

		self.SetSizer(vbox)

	def OnStart(self,e):
		global nodelist,peerlist
		print "Testing platform for the zeitcoin network"
		ampport=1234
		jsonrpcport=7080
		zn=zeitnetwork()
		peernum=int(self.tc.GetValue())
		startingport=int(self.tca.GetValue())
		str1=''
		self.cb2a.Clear()
		self.cb2a.Append(str(ampport))
		for i in range(startingport,startingport+peernum):
			str1+=str(i)+"\n"
			self.cb2a.Append(str(i))
		self.tc2a.SetValue(str1) 
		zn.parameters()
		zn.startservers(ampport,jsonrpcport)
		peerlist=zn.createpeers(peernum,startingport)
		zn.refreshingdb(peerlist)
		zn.initpeers(peerlist)
		nodelist=zn.createnetwork(peerlist)
		#reactor.run()
		return

	def OnStop(self,e):
		zn=zeitnetwork()
		zn.destorynetwork()
		return

	def OnSend(self, e):
		arglist=[]
		address='127.0.0.1'
		com1=self.cb2.GetValue()
		peer=self.cb2a.GetValue()
		data1=self.tc2d.GetValue()
		data2=self.tc2e.GetValue()
		data3=self.tc2f.GetValue()
		port=int(peer)
		cc=clientcommands()
		zn=zeitnetwork()
		if (com1=='getguid'):
			cc.dogetguid(address,port)
		elif (com1=='ping'):
			cc.doping(address,port,data1)
		elif (com1=='donetourguide'):
			cc.dodonetourguide(address,port)
		elif (com1=='copyht'):
			cc.docopyht(address,port)
		elif (com1=='getclosest'):
			cc.dogetclosest(address,port,data1)
		elif (com1=='getclosestpeer'):
			cc.dogetclosest(address,port,data1)
		elif (com1=='sendpublickey'):
			cc.dosendpublickey(address,port)
		elif (com1=='join'):
			cc.dojoin(address,port)
		elif (com1=='sendtotg'):
			ut=utility(FILENAME,ADDRESS,PORT)
			ts=ut.gettimestamp()
			cc.dosendtotg(address,port,data1,data2,4,data3,ts)
		elif (com1=='boardcasttrans'):
			cc.doboardcasttrans(address,port,'7','th966',111.12)
		elif (com1=='generatecoin'):
			cc.dogeneratecoin(address,port)
		elif (com1=='getnumtb'):
			cc.dogetnumtb(address,port)
		elif (com1=='encryptdata'):
			cc.doencryptdata(address,port,str(data1))
		elif (com1=='getnewaddress'):
			cc.dogetnewaddress(address,port,str(data1))
		elif (com1=='getleader'):
			cc.dogetleader(address,port,data1)
		elif (com1=='setleader'):
			cc.dosetleader(address,port,data1)
		elif (com1=='sendtransaction'):
			cc.dosendtransaction(address,port,data1,data2,data3)
		elif (com1=='gettransaction'):
			cc.dogettransaction(address,port)
		elif (com1=='getpuzzle'):
			ut=utility(FILENAME,ADDRESS,PORT)
			cc.dogetpuzzle(address,port,'1111','ho1111111',1111.22,5,'arr1arr2')
		elif (com1=='verifypuzzle'):
			ut=utility(FILENAME,ADDRESS,PORT)
			cc.doverifypuzzle(address,port,'2222','h11111','h222222')
		elif (com1=='acceptcoin'):
			ut=utility(FILENAME,ADDRESS,PORT)
			cc.doacceptcoin(address,port,'2','3333',111.11)
		elif (com1=='updatetb'):
			ut=utility(FILENAME,ADDRESS,PORT)
			cc.doupdatetb(address,port,'4444')
		elif (com1=='leave'):
			cc.doleave(address,port,guid)
		elif (com1=='leaderinfo'):
			ut=utility(FILENAME,ADDRESS,PORT)
			cc.doleaderinfo(address,port,'2222','127.0.0.1',1234)
		elif (com1=='initleader'):
			cc.doinitleader(address,port)
		elif (com1=='getbalance'):
			print "sending a getbalance JSON-RPC command"
			zn.testjsonrpc('getbalance',address,port+1000,arglist)
		elif (com1=='newaddress'):
			print "sending a newaddress JSON-RPC command"
			account=self.tc2d.GetValue()
			#data2=self.tc2e.GetValue()
			#data3=self.tc2f.GetValue()
			arglist.append(account)
			zn.testjsonrpc('newaddress',address,port+1000,arglist)
		elif (com1=='getaccountbalance'):
			print "sending a getaccountbalance JSON-RPC command"
			account=self.tc2d.GetValue()
			arglist.append(account)
			zn.testjsonrpc('getaccountbalance',address,port+1000,arglist)
		elif (com1=='getaccount'):
			print "sending a getaccount JSON-RPC command"
			transaddress=self.tc2d.GetValue()
			arglist.append(transaddress)
			zn.testjsonrpc('getaccount',address,port+1000,arglist)
		elif (com1=='getaddress'):
			print "sending a getaddress JSON-RPC command"
			account=self.tc2d.GetValue()
			arglist.append(account)
			zn.testjsonrpc('getaddress',address,port+1000,arglist)
		elif (com1=='sendcoins'):
			print "sending a sendcoins JSON-RPC command"
			zn.testjsonrpc('sendcoins',address,port+1000,arglist)
		elif (com1=='gettransaction'):
			print "sending a gettransaction JSON-RPC command"
			thash=self.tc2d.GetValue()
			arglist.append(thash)
			zn.testjsonrpc('gettransaction',address,port+1000,arglist)
		elif (com1=='isintour'):
			print "sending a isintour JSON-RPC command"
			zn.testjsonrpc('isintour',address,port+1000,arglist)		
		elif (com1=='istourguide'):
			print "sending a istourguide JSON-RPC command"
			zn.testjsonrpc('istourguide',address,port+1000,arglist)			
		elif (com1=='isleader'):
			print "sending a isleader JSON-RPC command"
			testjsonrpc('isleader',address,port+1000,arglist)			
		elif (com1=='listtransaction'):
			print "sending a listtransaction JSON-RPC command"
			startingtrans=self.tc2d.GetValue()
			numtrans=self.tc2e.GetValue()
			arglist.append(startingtrans)
			arglist.append(numtrans)
			zn.testjsonrpc('listtransaction',address,port+1000,arglist)			
		elif (com1=='listaccounttransaction'):
			print "sending a listaccounttransaction JSON-RPC command"
			account=self.tc2d.GetValue()
			arglist.append(account)
			zn.testjsonrpc('listaccounttransaction',address,port+1000,arglist)		
		elif (com1=='listaddresstransaction'):
			print "sending a listaddresstransaction JSON-RPC command"
			transaddress=self.tc2d.GetValue()
			arglist.append(transaddress)
			zn.testjsonrpc('listaddresstransaction',address,port+1000,arglist)			
		elif (com1=='backupwallet'):
			print "sending a backwallet JSON-RPC command"
			zn.testjsonrpc('backwallet',address,port+1000,arglist)			
		elif (com1=='Show wallet table'):
			db=dbcommands()
			db.showwallet(peer)
		elif (com1=='Show hash table'):
			db=dbcommands()
			db.showhash(peer)			
		elif (com1=='Show transaction block table'):
			db=dbcommands()
			db.showtb(peer)			
		elif (com1=='Show transaction local table'):
			db=dbcommands()
			db.showtl(peer)
		elif (com1=='Show accounts table'):
			db=dbcommands()
			db.showaccounts(peer)			
		elif (com1=='Show leader tabled'):
			db=dbcommands()
			db.showleader(peer)
		else:
			pass			
		return

	def OnSelect(self, e):
		com1 = e.GetString()
		#print "select"
		if (com1=='getguid'):
			self.hidedata()
		elif (com1=='ping'):
			self.hidedata()
		elif (com1=='copyht'):
			self.hidedata()
		elif (com1=='donetourguide'):
			self.hidedata()
		elif (com1=='getclosest'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("GUID")
		elif (com1=='getclosestpeer'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("GUID")
		elif (com1=='sendpublickey'):
			self.hidedata()
		elif (com1=='join'):
			self.hidedata()
		elif (com1=='sendtotg'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			hashvalue=ut.generateguid()
			self.hidedata2()
			self.tc2d.SetValue(hashvalue) 
			self.st2d.SetLabel("Hashvalue")
			self.tc2e.SetValue(guid) 
			self.st2e.SetLabel("GUID")
			self.tc2f.SetValue('1') 
			self.st2f.SetLabel("Stopnumber")
		elif (com1=='boardcasttrans'):
			self.hidedata()
		elif (com1=='generatecoin'):
			self.hidedata()
		elif (com1=='getnumtb'):
			self.hidedata()
		elif (com1=='encryptdata'):
			self.hidedata1()
			self.tc2d.SetValue('message') 
			self.st2d.SetLabel("Message")
		elif (com1=='getnewaddress'):
			self.hidedata1()
			self.tc2d.SetValue('user1') 
			self.st2d.SetLabel("Account")
		elif (com1=='getleader'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata2()
			self.tc2d.SetValue('127.0.0.1') 
			self.st2d.SetLabel("Client Address")
			self.tc2e.SetValue('3000') 
			self.st2e.SetLabel("Client Port")
			self.tc2f.SetValue(guid) 
			self.st2f.SetLabel("GUID")
		elif (com1=='setleader'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata2()
			self.tc2d.SetValue('127.0.0.1') 
			self.st2d.SetLabel("Client Address")
			self.tc2e.SetValue('3000') 
			self.st2e.SetLabel("Client Port")
			self.tc2f.SetValue(guid) 
			self.st2f.SetLabel("GUID")
		elif (com1=='sendtransaction'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			guid1=ut.generateguid()
			self.hidedata2()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("Coinhash")
			self.tc2e.SetValue(guid1) 
			self.st2e.SetLabel('ReceiverAddress')
			self.tc2f.SetValue('message') 
			self.st2f.SetLabel("Message")
		elif (com1=='gettransaction'):
			self.hidedata()
		elif (com1=='getpuzzle'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.ut.generateguid()
			h0=ut.getguid()
			ts=ut.gettimestamp()
			self.hidedata2()
			self.tc2d.SetValue(hashvalue) 
			self.st2d.SetLabel("H0")
			self.tc2e.SetValue(guid) 
			self.st2e.SetLabel("GUID")
			self.tc2f.SetValue('5') 
			self.st2f.SetLabel("Length")
		elif (com1=='verifypuzzle'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.ut.generateguid()
			h0=ut.generateguid()
			ts=ut.gettimestamp()
			self.hidedata2()
			self.tc2d.SetValue(hashvalue) 
			self.st2d.SetLabel("H0")
			self.tc2e.SetValue(guid) 
			self.st2e.SetLabel("GUID")
			self.tc2f.SetValue('5') 
			self.st2f.SetLabel("Length")
		elif (com1=='acceptcoin'):
			ut=utility(FILENAME,ADDRESS,PORT)
			txid=ut.generateguid()
			thash=ut.generateguid()
			ts=ut.gettimestamp()
			self.hidedata2()
			self.tc2d.SetValue(txid) 
			self.st2d.SetLabel("txid")
			self.tc2e.SetValue(thash) 
			self.st2e.SetLabel("thash")
			self.tc2f.SetValue(str(ts)) 
			self.st2f.SetLabel("timestamp")
		elif (com1=='updatetb'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("thash")
		elif (com1=='leave'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("GUID")
		elif (com1=='leaderinfo'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata2()
			self.tc2d.SetValue('127.0.0.1') 
			self.st2d.SetLabel("Client Address")
			self.tc2e.SetValue('3000') 
			self.st2e.SetLabel("Client Port")
			self.tc2f.SetValue(guid) 
			self.st2f.SetLabel("GUID")
		elif (com1=='initleader'):
			self.hidedata()
		elif (com1=='getbalance'):
			self.hidedata()
		elif (com1=='newaddress'):
			self.hidedata1()
			self.tc2d.SetValue('user1') 
			self.st2d.SetLabel("Account")
		elif (com1=='getaccountbalance'):
			self.hidedata1()
			self.tc2d.SetValue('user1') 
			self.st2d.SetLabel("Account")
		elif (com1=='getaccount'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("Address")
		elif (com1=='getaddress'):
			self.hidedata1()
			self.tc2d.SetValue('user1') 
			self.st2d.SetLabel("Account")
		elif (com1=='sendcoins'):
			self.hidedata()
		elif (com1=='gettransaction'):
			ut=utility(FILENAME,ADDRESS,PORT)
			guid=ut.generateguid()			
			self.hidedata1()
			self.tc2d.SetValue(guid) 
			self.st2d.SetLabel("Account")
		elif (com1=='isintour'):
			self.hidedata()
		elif (com1=='istourguide'):
			self.hidedata()
		elif (com1=='isleader'):
			self.hidedata()
		elif (com1=='listtransaction'):
			self.st2d.Show()
			self.tc2d.Show()
			self.st2e.Show()
			self.tc2e.Show()
			self.st2f.Hide()
			self.tc2f.Hide()
			self.tc2d.SetValue('1') 
			self.st2d.SetLabel("Starting Transaction")
			self.tc2e.SetValue('3') 
			self.st2e.SetLabel("Number of Transactions")
		elif (com1=='listaccounttransaction'):
			self.hidedata1()
			self.tc2d.SetValue('user1') 
			self.st2d.SetLabel("Account")
		elif (com1=='listaddresstransaction'):
			ut=utility(FILENAME,ADDRESS,PORT)
			thash=ut.generateguid()
			self.hidedata1()
			self.tc2d.SetValue(thash) 
			self.st2d.SetLabel("Address")
		elif (com1=='backupwallet'):
			self.hidedata()
		elif (com1=='Show wallet table'):
			self.hidedata()
		elif (com1=='Show hash table'):
			self.hidedata()
		elif (com1=='Show transaction block table'):
			self.hidedata()
		elif (com1=='Show transaction local table'):
			self.hidedata()
		elif (com1=='Show accounts table'):
			self.hidedata()
		elif (com1=='Show leader tabled'):
			self.hidedata()
		else:
			self.hidedata()
		return

	def hidedata(self):
		self.st2d.Hide()
		self.tc2d.Hide()
		self.st2e.Hide()
		self.tc2e.Hide()
		self.st2f.Hide()
		self.tc2f.Hide()
		return

	def hidedata1(self):
		self.st2d.Show()
		self.tc2d.Show()
		self.st2e.Hide()
		self.tc2e.Hide()
		self.st2f.Hide()
		self.tc2f.Hide()
		return

	def hidedata2(self):
		self.st2d.Show()
		self.tc2d.Show()
		self.st2e.Show()
		self.tc2e.Show()
		self.st2f.Show()
		self.tc2f.Show()
		return

	def OnClear(self,e):
		self.tc2.SetValue('') 
		return

	def Setamp(self, e):
		self.cb2.Clear()
		self.cb2.Append('ping')
		self.cb2.Append('getguid')
		self.cb2.Append('donetourguide')
		self.cb2.Append('copyht')
		self.cb2.Append('getclosest')
		self.cb2.Append('getclosestpeer')
		self.cb2.Append('sendpublickey')
		self.cb2.Append('join')
		self.cb2.Append('sendtotg')
		self.cb2.Append('boardcasttrans')
		self.cb2.Append('generatecoin')
		self.cb2.Append('getnumtb')
		self.cb2.Append('encryptdata')
		self.cb2.Append('getnewaddress')
		self.cb2.Append('getleader')
		self.cb2.Append('setleader')
		self.cb2.Append('sendtransaction')
		self.cb2.Append('getpuzzle')
		self.cb2.Append('verifypuzzle')
		self.cb2.Append('acceptcoin')
		self.cb2.Append('updatetb')
		self.cb2.Append('leave')
		self.cb2.Append('leaderinfo')
		self.cb2.Append('initleader')
		return

	def Setjsonrpc(self, e):
		self.cb2.Clear()
		self.cb2.Append('getbalance')
		self.cb2.Append('newaddress')
		self.cb2.Append('getaccountbalance')
		self.cb2.Append('getaccount')
		self.cb2.Append('getaddress')
		self.cb2.Append('sendcoins')
		self.cb2.Append('gettransaction')
		self.cb2.Append('isintour')
		self.cb2.Append('istourguide')
		self.cb2.Append('isleader')
		self.cb2.Append('listtransaction')
		self.cb2.Append('listaccounttransaction')
		self.cb2.Append('listaddresstransaction')
		self.cb2.Append('backupwallet')
		return

	def Setdatabase(self, e):
		self.cb2.Clear()
		self.cb2.Append('Show wallet table')
		self.cb2.Append('Show hash table')
		self.cb2.Append('Show transaction block table')
		self.cb2.Append('Show transaction local table')
		self.cb2.Append('Show accounts table')
		self.cb2.Append('Show leader tabled')
		return


class ChangeOptions(wx.Dialog):
    
    def __init__(self, *args, **kw):
	super(ChangeOptions, self).__init__(*args, **kw) 
	self.InitUI()
	self.SetSize((250, 200))
	self.SetTitle("Change Options")
		
		
    def InitUI(self):
	global PORT
	font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
	font.SetPointSize(10)

	pnl = wx.Panel(self)
	vbox = wx.BoxSizer(wx.VERTICAL)

	sb = wx.StaticBox(pnl, label='Options')
	sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)   

	hbox1 = wx.BoxSizer(wx.HORIZONTAL)
	st1 = wx.StaticText(pnl, label='Port ')
	st1.SetFont(font)
	hbox1.Add(st1, flag=wx.RIGHT)
	self.tc1 = wx.TextCtrl(pnl,-1,str(PORT))
	hbox1.Add(self.tc1, proportion=1)     
		
	sbs.Add(hbox1)
		
	pnl.SetSizer(sbs)
	       
	hbox2 = wx.BoxSizer(wx.HORIZONTAL)
	okButton = wx.Button(self, label='Ok')
	closeButton = wx.Button(self, label='Close')
	hbox2.Add(okButton)
	hbox2.Add(closeButton, flag=wx.LEFT, border=5)

	vbox.Add(pnl, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
	vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

	self.SetSizer(vbox)
		
	okButton.Bind(wx.EVT_BUTTON, self.OnChangePort)
	closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
		
    def OnChangePort(self, e):
	global PORT
	port=self.tc1.GetValue()
	PORT=port
	self.Destroy()
	return	
	
    def OnClose(self, e): 
	self.Destroy()

class dbcommands:

	@defer.deferredGenerator
	def showwallet(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Wallet table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetallwallet(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def showhash(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Hash table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetallht(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def showtb(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Block transaction table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetalltb(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def showtl(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Local transaction table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetalltb(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def showaccounts(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Accounts table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetallaccount(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

	@defer.deferredGenerator
	def showleader(self,port):
		global FNAME,PORT,peerlist
		print "port=",port
		if (int(port)==PORT):
			db=FNAME
			address='127.0.0.1'
		else:
			for peer in peerlist:
				if (peer[1]==port):
					db="./test/"+str(peer[3])
					address=peer[0]
		print "=====Leader table for "+str(address)+":"+str(port)+"=====\n"
		ht=hashtable()
		dbpool=ht.tconnectdb(db)
		wfd = defer.waitForDeferred(ht.tgetallleader(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			print str(i)+"\n"
		ht.tclosedb(dbpool)
		return

class zeitnetwork:

	def startservers(self,ampport,jsonrpcport): 
		# Start the amp server
		global PORT
		zt=Zeit
		pf = Factory()
		pf.protocol = zt
		reactor.listenTCP(ampport, pf)
		reactor.listenTCP(jsonrpcport, server.Site(zeitjsonrpc()))

	def createpeers(self,peernum,startingport):
		global ADDRESS,PORT,FNAME
		ut=utility(FNAME,ADDRESS,PORT)
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

	def initpeers(self,peerlist):
		balance=0
		for peer in peerlist:
			time1=time.time()
			file1=peer[3]
			guid1=peer[2]
			self.createkeys1(file1)
			self.copydb(file1)
			db="./test/"+str(file1)+".db"
			conn = sqlite3.connect(db)
			c = conn.cursor()
			c.execute("INSERT INTO wallet VALUES ('"+str(guid1)+"','"+str(balance)+"','"+str(time1)+"')")
			conn.commit()
			c.execute("DELETE from hashtable where guid='"+guid1+"'")
			conn.commit()
			conn.close()
		return

	def parameters(self):
		# checking for file and inital data and set the up if they don't exit
		# check for database file and if don't exist set up the hash table based on address,port given
		global FNAME
		dbname=FNAME+".db"
		pubname=FNAME+"-public.pem"
		if (os.path.isfile(dbname)==False):
			print "Creating the database"
			self.createdb()
		if (os.path.isfile(pubname)==False):
			print "Creating the public and private keys"
			self.createkeys()
		return

	def refreshingdb(self,htlist):
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

	def createkeys1(self,file1):
		file1="./test/"+file1
		en=encyption()
		en.generatewalletkeys(file1)
		return

	def copydb(self,file1):
		file1= "./test/"+file1+".db"
		shutil.copy2('zeitcoin.db', file1)
		return

	def destorynetwork(self):
		global nodelist
		print "Shutting down the Network....."
		for node in nodelist:
			node.terminate()
		print "Finish with the Network"
		return

	def createnetwork(self,peerlist):
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

	def printValue(self,value):
    		print "Result: %s" % str(value)

	def printError(self,error):
    		print 'error', error

	def shutDown(self,data):
    		print "finish with the JSON-RPC command..."

	def testjsonrpc(self,com1,address,port,arglist):
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
		d.addCallback(self.printValue).addErrback(self.printError).addBoth(self.shutDown)

class RedirectText:
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl

	def write(self,string):
		self.out.WriteText(string)

class MyApp(App):
	
    def OnInit(self):
	zeitnet()
        # look, we can use twisted calls!
        #reactor.callLater(5, self.fiveSecondsPassed)
        return True

		

def main():
	app = MyApp(0)
	reactor.registerWxApp(app)
        reactor.run()

if __name__ == '__main__':
    main()

# Database Structure:
# Table blocktrans: txid, thash, timestamp (separte db)
# ==========================================================
# Table hasttable : guid, address, port, flag, timestamp
# Table localtrans: txid, thash, walletaddress, otheraddress, amount, type, timestamp		
# Table account   : address, privkey, pubkey, account
# Table leader    : sharedkey, address, port, guid, timestamp
# Table Wallet    : guid, balance, timestamp

# Protocol:
# 1) Getleader
# -> Dogetleader - is sent by the client to a random peer (rpeer) 
# <- Getleader - will send back an 'ok' response to the client
# -> Dosetleader - is sent from rpeer to lpeer(another random peer determine by rpeer) which tells lpeer to be the leader #                  and gives it the client info to lpeer.  Also lpeer will then find the guide tours for this client
# <- Setleader(branch 1b) - lpeer will send by an 'ok' response to rpeer
# -> doleaderinfo rpeer will send to the client the leader (lpeer) address, port and guid
# <- leaderinfo  the client will send back an 'ok' response to rpeer
# ------Pause until donetourguide message is received -----------
# -> Dogettransaction - rpeer request transaction from the client
# <- gettransaction - client responds back with the transaction
# -> DosendTransaction - rpeer sends lpeer the transaction
# <- Sendtransaction - lpeer will reply with an 'ok' message
# -> doinitleader -> rpeer will send an 'init' message to to lpeer
# <- initleader -> lpeer will send back an 'ok' message to rpeer
# -> dogetpuzzle - is then sent from lpeer back to the client (h0,ts,L,arraytg) After it finish with getting the tour guide #                  information.  Each verify each info 
# <- getpuzzle - is return to lpeer a sucessful reply
#
# -------> Branch 1b: Gettourguides (when a leader has been chosen with the setleader command lpeer)
# -------> 1) The leader will choose N many tour guides from its hashtable
# -------> 2) Dosendpublickey - is sent to each tour guide.  This will set the tour guide and reply with its public key
#--------> 3) Sendpublickey - sends back its public key to the leader
# -------> 4) Dodonetourguides - After gathering the tour guides send back to rpeer that it is done
# -------> 5) Donetourguide - rpeer will send back an 'ok' message
#
# 2) Gettourguides
# -> The leader (lpeer) will randomly choose N many tour guides from its hash table
# -> Dosendpublickey - is sent to each tour guide.  This will set the tour guide and it will reply with its public key
# -> After each tour guide as responded back the information will be stored in array (arraytg)
#
# 3)Tour Guide
# -> After receiving the puzzle.  The client use h0 and calculate the tour guide index
# -> Dosendtg - Will be sent to the appropriate tour guid with the hash, stopnumber and L
# -> Sendtg - will be the response after verifing the information. It will have the new hash (H0)
# -> The client will keeping contacting the tour guides until stop number reaches L.  Tour is over
# -> Doverifypuzzle - is send from the client back to the leader
# -> Verifypuzzle - will reply with a true or false after checking the data.
# -> After which the transaction is stored in the block and boardcast to all the peers
#
# 4) A new peer joins
# -> Dogetuuid - is send to a peer on the network
# -> Getuuid - will be replied back to the client with the new guid for the new peer.  It will be stored in the db
# -> Docopyht - the client will then send this command to the peer as before
# -> Copyht - the peer will store the new guid in its hashtable and send back a copy of its hash table to the new peer
# -> The new peer will use the copy hash table to generate its own value for the table
#
# 5) Update transaction block (once an hour)
# -> DoGetnumtb - Will be sent by the client to everyone on its hash table.
# -> Getnumtb - Will return back to the client the number of transaction in its block
# -> The client will find the highest number sent back to it and contact the client that sent it
# -> DoUpdatetb - will be sent with its most recent txid from the client to the peer with the highest number
# -> Updatetb - Will send back its most recent transaction and its index back to the client
# -> if the number in the client transaction block is lower than the highest number than the process is repeated
#
# 6) Ping (once an hour)
# -> Doping - will be sent back from the client to every peer on its hash table
# -> Ping - is send by to the client with the reply 'hello'
# -> whoever does not respond back gets its flag set and is the next to be delete from the hash table if space is needed
#
# 7) Leave
# -> Doleave - Will be sent from the client when it is leaving the network, to every peer on its hash table
# -> Leave - Will respond back from each peer with the reply of 'ok'
#
# 8) Broadcast - Will be sent to everyone on the network.  New transaction blocks
# -> Doboardcast - Will be sent by the client to its closest peer and its farest peer
# -> Boardcast - the peers will reply back with OK to the client and in turn boardcast out themselves
#
# 9) Getclosestpeer - to a particular guid
# -> DoGetclosestpeer - is sent from the client to its closest peer on the clients hash table
# -> Getclosest peer - will reply back to the client the closest peer on its hash table
# -> This is repeated until the closest peer on the network is founded. 
#
#10) Getclosest - Gets the closest peer in the peer hash table
# -> Dogetclosest - send from client to another peer to get the peer closest guid in its hash table
# -> Getclosest - replys back to the client the closest peer in its hash table
#
#11) Getfarest - Gets the farest peer in the peer hash table
# -> Dogetfarest - send from client to another peer to get the peer farest guid in its hash table
# -> Getfarest - replys back to the client the farest peer in its hash table
#
#12) Sendcoin - Sends a coin to an address
# -> The peer finds a coin it can spend
# -> Transpose the sending transaction to the correct format and stored it temporary 
# -> Initiate a guided tour
#
#13) Generate new coin 
# -> doGeneratecoin - is called every X many transaction.  The client will send this to a random peer
# -> Generatecoin - This peer will generate a new coin address and send it to another random peer.  Reply with Ok
# -> doacceptcoin - is sent to the random peer and the random peer will accept the coin and broadcast it out
# -> acceptcoin - Replys back with OK, the sender peer will also store transaction and boardcast it out
