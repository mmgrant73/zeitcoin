#!/usr/bin/python
######################
# Zeitcoin Wallet GUI
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

FNAME='zeitcoin'
BALANCE=9
GUID=''
PORT=1234
ADDRESS='127.0.0.1'

class wallet(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Zietcoin Wallet")

	self.panelhome = PanelHome(self)
        self.panelsend = PanelSend(self)
	self.panelaccount = PanelAccount(self)
	self.paneltransaction = PanelTransaction(self)
	self.panelhome.Show()
        self.panelsend.Hide()
	self.panelaccount.Hide()
	self.paneltransaction.Hide()
	self.panelhome.updatebalance()
	self.panelaccount.getaccounts()

	self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelhome, 1, wx.EXPAND)
        self.sizer.Add(self.panelsend, 1, wx.EXPAND)
	self.sizer.Add(self.panelaccount, 1, wx.EXPAND)
	self.sizer.Add(self.paneltransaction, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

	toolbar = self.CreateToolBar()
        htool = toolbar.AddLabelTool(wx.ID_ANY, 'Home', wx.Bitmap('./images/home.jpg'))
	stool = toolbar.AddLabelTool(wx.ID_ANY, 'Send', wx.Bitmap('./images/send.jpg'))
	atool = toolbar.AddLabelTool(wx.ID_ANY, 'Accounts', wx.Bitmap('./images/account.jpg'))
	ttool = toolbar.AddLabelTool(wx.ID_ANY, 'Transactions', wx.Bitmap('./images/transaction.jpg'))
        toolbar.Realize()

	self.Bind(wx.EVT_TOOL, self.OnHome, htool)
	self.Bind(wx.EVT_TOOL, self.OnSend, stool)
	self.Bind(wx.EVT_TOOL, self.OnAccount, atool)
	self.Bind(wx.EVT_TOOL, self.OnTransaction, ttool)

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
	settingsMenu = wx.Menu()
	helpMenu = wx.Menu()

        self.shbackup=fileMenu.Append(wx.ID_ANY, '&Backup Wallet')
        fileMenu.AppendSeparator()

        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Exit\tCtrl+W')
        fileMenu.AppendItem(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
	self.Bind(wx.EVT_MENU, self.OnBackup, self.shbackup)

	self.shwallet=settingsMenu.Append(wx.ID_ANY, '&Wallet Info')
        settingsMenu.AppendSeparator()
	self.shoption=settingsMenu.Append(wx.ID_ANY, '&Options')

	self.Bind(wx.EVT_MENU, self.ShowWalletInfo,self.shwallet)
	self.Bind(wx.EVT_MENU, self.ShowOption,self.shoption)

	self.shhelp=helpMenu.Append(wx.ID_ANY, '&Help')
        helpMenu.AppendSeparator()
	self.shabout=helpMenu.Append(wx.ID_ANY, '&About')

	self.Bind(wx.EVT_MENU, self.OnHelp, self.shhelp)
	self.Bind(wx.EVT_MENU, self.OnAboutBox, self.shabout)

        menubar.Append(fileMenu, '&File')
	menubar.Append(settingsMenu, '&Settings')
	menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)

        self.SetSize((600, 400))
        self.SetTitle('Zeitcoin-Wallet: Overview')
        self.Centre()
        self.Show(True)

    @defer.deferredGenerator
    def ShowWalletInfo(self, e):
	global FNAME,PORT,ADDRESS
	ht=hashtable()
	dbpool=ht.tconnectdb(FNAME)
	wfd = defer.waitForDeferred(ht.tgetguid(dbpool))
	yield wfd
	guid = str(wfd.getResult()) #ht.tgetbalance
	wfd = defer.waitForDeferred(ht.tgetbalance(guid,dbpool))
	yield wfd
	balance = str(wfd.getResult())
	ht.tclosedb(dbpool)
	str1="Balance - "+str(balance)+"\n"
	str1+="Guid - "+str(guid)+"\n"
	str1+="Address - "+str(ADDRESS)+"\n"
	str1+="Port - "+str(PORT)+"\n"
        wx.MessageBox(str1, 'Wallet Information', wx.OK | wx.ICON_INFORMATION)
	return

    def ShowOption(self, e):
        #wx.MessageBox('Option', 'Options', wx.OK | wx.ICON_INFORMATION)
	chgopt = ChangeOptions(None, title='Change Wallet Options')
        chgopt.ShowModal()
        chgopt.Destroy() 
	return

    def OnHome(self, e):
        self.SetTitle("Zeitcoin-Wallet: Overview")
        self.panelhome.Show()
        self.panelsend.Hide()
	self.panelaccount.Hide()
	self.paneltransaction.Hide()
	self.panelhome.updatebalance()
	#self.panelhome.st1.SetLabel("Oh, this is very looooong!")
        self.Layout()
        # self.panel.Layout()  #Either works
	return

    def OnSend(self, e):
        self.SetTitle("Zeitcoin-Wallet: Send")
        self.panelhome.Hide()
        self.panelsend.Show()
	self.panelaccount.Hide()
	self.paneltransaction.Hide()
        self.Layout()
	return

    def OnAccount(self, e):
        self.SetTitle("Zeitcoin-Wallet: Accounts")
        self.panelhome.Hide()
        self.panelsend.Hide()
	self.panelaccount.Show()
	self.paneltransaction.Hide()
        self.Layout()
	return

    def OnTransaction(self, e):
        self.SetTitle("Zeitcoin-Wallet: Transactions")
        self.panelhome.Hide()
        self.panelsend.Hide()
	self.panelaccount.Hide()
	self.paneltransaction.Show()
        self.Layout()
	return
        
    def OnQuit(self, e):
	reactor.stop()
        self.Close()

    def OnHelp(self, e):
	HelpWindow(None,-1,'Zeitcoin Wallet Help')

    def OnBackup(self, e):
	backupfile = wx.SaveFileSelector('Backup of the Zeitcoin Database', '.db', 'zeitcoinbackup.db', None)
	return

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
        info.SetName('Zeitcoin Wallet')
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

class PanelSend(wx.Panel):

    	def __init__(self, parent):
        	wx.Panel.__init__(self, parent=parent)

		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(14)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, label='Send Coins')
		st.SetFont(font)
		hbox.Add(st, flag=wx.RIGHT, border=20)

		vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		vbox.Add((-1, 5))

		font.SetPointSize(10)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, label='Balance: ')
		st1.SetFont(font)
		hbox1.Add(st1, flag=wx.RIGHT, border=20)

		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 5))

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		st2 = wx.StaticText(self, label='Amount to be sent ')
		st2.SetFont(font)
		hbox2.Add(st2, flag=wx.RIGHT, border=20)
		tc2 = wx.TextCtrl(self)
                hbox2.Add(tc2, proportion=1)

		vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 2))

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		st3 = wx.StaticText(self, label='Zeitcoin Address   ')
		st3.SetFont(font)
		hbox3.Add(st3, flag=wx.RIGHT, border=20)
		tc3 = wx.TextCtrl(self)
                hbox3.Add(tc3, proportion=1)

		vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 2))

		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		st4 = wx.StaticText(self, label='Message ')
		st4.SetFont(font)
		hbox4.Add(st4, flag=wx.RIGHT, border=20)

		vbox.Add(hbox4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 4))

		hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		tc5 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		hbox5.Add(tc5, proportion=1, flag=wx.EXPAND)

		vbox.Add(hbox5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 2))

		hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        	btn6 = wx.Button(self, label='Send', size=(70, 30))
        	hbox6.Add(btn6)
        	
		vbox.Add(hbox6, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)
		
		self.SetSizer(vbox)

class PanelAccount(wx.Panel):

    	def __init__(self, parent):
        	wx.Panel.__init__(self, parent=parent)

		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(14)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, label='Account Information')
		st.SetFont(font)
		hbox.Add(st, flag=wx.RIGHT, border=130)

		vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		font.SetPointSize(10)

		vbox.Add((-1, 5))

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, label='Accounts ')
		st1.SetFont(font)
		hbox1.Add(st1, flag=wx.RIGHT, border=20)

		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 2))

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.tc2 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		hbox2.Add(self.tc2, proportion=1, flag=wx.EXPAND)

		vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 30))

		font.SetPointSize(12)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		st3 = wx.StaticText(self, label='Add a new account ')
		st3.SetFont(font)
		hbox3.Add(st3, flag=wx.RIGHT, border=20)

		vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		font.SetPointSize(10)

		vbox.Add((-1, 5))

		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		st4 = wx.StaticText(self, label='Account Name ')
		st4.SetFont(font)
		hbox4.Add(st4, flag=wx.RIGHT, border=20)
		self.tc4 = wx.TextCtrl(self)
                hbox4.Add(self.tc4, proportion=1)

		vbox.Add(hbox4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		vbox.Add((-1, 5))

		hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        	btn5 = wx.Button(self, label='Add', size=(70, 30))
        	hbox5.Add(btn5)
        	
		vbox.Add(hbox5, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)

		btn5.Bind(wx.EVT_BUTTON, self.OnAddAccount)

		self.SetSizer(vbox)

	@defer.deferredGenerator
	def OnAddAccount(self, e):
		ht=hashtable()
		en=encyption()
		ut=utility()
		time1=ut.gettimestamp()
		address=ut.generateguid()
		pubkey,privkey=en.generatekeys()
		account=self.tc4.GetValue()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.taddaccount(dbpool,account,privkey,pubkey,address,time1))
		yield wfd
		ht.tclosedb(dbpool)
		self.getaccounts()
		return 

	@defer.deferredGenerator
	def getaccounts(self):
		global FNAME
		str1=''
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetallaccount(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			str1+=str(i[3])+" - "+str(i[0])+"\n"
		ht.tclosedb(dbpool)
		self.tc2.SetValue(str1) 
		return

class PanelTransaction(wx.Panel):

    	def __init__(self, parent):
        	wx.Panel.__init__(self, parent=parent)

		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(14)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, label='Transaction')
		st.SetFont(font)
		hbox.Add(st, flag=wx.RIGHT, border=130)

		vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		font.SetPointSize(10)

		vbox.Add((-1, 5))

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.tc1 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		hbox1.Add(self.tc1, proportion=1, flag=wx.EXPAND)

		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		self.SetSizer(vbox)

	@defer.deferredGenerator
	def gettransaction(self):
		global FNAME
		str1=''
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetalllt(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			str1+=str(i[3])+" - "+str(i[4])+" - "+str(i[5])+" - "+str(i[6])+"\n"
		ht.tclosedb(dbpool)
		self.tc2.SetValue(str1) 
		return


class PanelHome(wx.Panel):
 
   	def __init__(self, parent):
		global BALANCE
        	wx.Panel.__init__(self, parent=parent)

		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(14)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, label='Overview')
		st.SetFont(font)
		hbox.Add(st, flag=wx.RIGHT, border=130)

		vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		font.SetPointSize(10)

		#sb = wx.StaticBox(self, label='Wallet Balance')
		#sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL) 

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.st1 = wx.StaticText(self, label='Balance:'+str(BALANCE))
		self.st1.SetFont(font)
		hbox1.Add(self.st1, flag=wx.RIGHT, border=240)
		sta = wx.StaticText(self, label='Recent Transactions')
		sta.SetFont(font)
		hbox1.Add(sta, proportion=1, flag=wx.EXPAND)

		#sbs.Add(hbox1)
		#self.SetSizer(sbs)

		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)

		vbox.Add((-1, 2))

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		st2 = wx.StaticText(self, label='Confirmation: 0')
		st2.SetFont(font)
		hbox2.Add(st2, flag=wx.RIGHT, border=100)
		tc2 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		hbox2.Add(tc2, proportion=1, flag=wx.EXPAND)

		vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		self.SetSizer(vbox)

	@defer.deferredGenerator
	def gettransactions():
		global FNAME
		str1=''
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetalllt(dbpool))
		yield wfd
		list1 = wfd.getResult()
		for i in list1:
			str1+=str(i[3])+" - "+str(i[4])+" - "+str(i[5])+" - "+str(i[6])+"\n"
		ht.tclosedb(dbpool)
		self.tc2.SetValue(str1) 
		return

	@defer.deferredGenerator
	def updatebalance(self):
		global FNAME,BALANCE,GUID
		ht=hashtable()
		dbpool=ht.tconnectdb(FNAME)
		wfd = defer.waitForDeferred(ht.tgetguid(dbpool))
		yield wfd
		GUID = str(wfd.getResult()) 
		wfd = defer.waitForDeferred(ht.tgetbalance(GUID,dbpool))
		yield wfd
		BALANCE = str(wfd.getResult())
		ht.tclosedb(dbpool)
		self.st1.SetLabel("Balance: "+str(BALANCE))
        	self.Layout()
		return

class HelpWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(570, 400))

	panel = wx.Panel(self)

	vbox2 = wx.BoxSizer(wx.VERTICAL)

        help = html.HtmlWindow(panel, -1, style=wx.NO_BORDER)
        help.LoadPage('./help.html')
        vbox2.Add(help, 1, wx.EXPAND)

	panel.SetSizer(vbox2)

        self.CreateStatusBar()

        self.Centre()
        self.Show(True)

    def OnClose(self, event):
        self.Close()

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

class MyApp(App):
	
    def fiveSecondsPassed(self):
        wx.MessageBox('5 seconds has passed', 'Test', wx.OK | wx.ICON_INFORMATION)
	return

    @defer.deferredGenerator
    def getinfo(self,d):
	global FNAME,BALANCE,GUID
	ht=hashtable()
	dbpool=ht.tconnectdb(FNAME)
	wfd = defer.waitForDeferred(ht.tgetguid(dbpool))
	yield wfd
	GUID = str(wfd.getResult()) #ht.tgetbalance
	wfd = defer.waitForDeferred(ht.tgetbalance(GUID,dbpool))
	yield wfd
	BALANCE = str(wfd.getResult())
	ht.tclosedb(dbpool)
	return

    def _getinfo(self):
	wallet()
	return
	
    def OnInit(self):
	wallet()
        # look, we can use twisted calls!
        #reactor.callLater(5, self.fiveSecondsPassed)
        return True

		

def main():
	app = MyApp(0)
	reactor.registerWxApp(app)
        reactor.run()

if __name__ == '__main__':
    main()


