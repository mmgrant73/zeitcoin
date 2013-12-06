#!/usr/local/bin/python

import sys, re, hashlib
from M2Crypto import Rand, RSA, BIO

class zeitforth:

	ds       = []          # The data stack
	cStack   = []          # The control struct stack
	heap     = [0]*20      # The data heap
	heapNext =  0          # Next avail slot in heap
	words    = []          # The input stream of tokens

	PUBKEY = 'zeitcoin-public.pem'

	#============================== Lexical Parsing

	def tokenizeWords(self,s) :                                         # clip comments, split to list of words
	    self.words += re.sub("#.*\n","\n",s+"\n").lower().split()  # Use "#" for comment to end of line
	    return

	#================================= Runtime operation

	def stripstr(self,str1):
		fletter = str1[0]
		lletter = str1[-1]
		if (fletter=='"' and lletter=='"'):
			str1 = str1[1:-1]
		return str1

	def execute (self,code) :
	    p = 0
	    while p < len(code) :
		func = code[p]
		p += 1
		newP = func(self,code,p)
		if newP != None : p = newP

	def rAdd (self,cod,p) : 
		try:
			b=self.ds.pop()
			a=self.ds.pop()
			resulta=isinstance( a, ( int, long ) )
			resultb=isinstance( b, ( int, long ) )
			if (resulta and resultb):
				self.ds.append(a+b)
			else:
				print "[error] - Can not use a string with this command"
				self.ds.append(0)
		except:
			print "[error] - Runtime error the shack is empty"
		return 

	def rMul (self,cod,p) : 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			self.ds.append(a*b)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return 

	def rSub (self,cod,p) : 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			self.ds.append(a-b)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return

	def rDiv (self,cod,p) : 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			self.ds.append(a/b)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return
	
	def rEq  (self,cod,p) : 
		try:
			b=self.ds.pop()
			a=self.ds.pop()
			resulta=isinstance( a, ( int, long ) )
			resultb=isinstance( b, ( int, long ) )
			if (resulta and resultb):
				self.ds.append(int(a==b))
			elif ((not(resulta)) and (not(resultb))):
				if (str(a)==str(b)):
					self.ds.append(1)
				else:
					self.ds.append(0)
			else:
				print "[error] - The data being compared must be of the same type"
				self.ds.append(0)
		except:
			print "[error] - Runtime error the shack is empty"
		return

	def rGt  (self,cod,p) : 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			self.ds.append(int(a>b))
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return

	def rLt  (self,cod,p) : 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			self.ds.append(int(a<b))
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return

	def rSwap(self,cod,p) : 
		a=self.ds.pop() 
		b=self.ds.pop()
		self.ds.append(a)
		self.ds.append(b)
		return

	def rDup (self,cod,p) : 
		self.ds.append(self.ds[-1])
		return

	def rDrop(self,cod,p) : 
		self.ds.pop()
		return

	def rOver(self,cod,p) : 
		self.ds.append(self.ds[-2])
		return

	def rDump(self,cod,p) : 
		print "ds = ", self.ds
		return

	def rDot (self,cod,p) : 
		print self.ds.pop()
		return

	def rJmp (self,cod,p) : 
		return cod[p]

	def rJnz (self,cod,p) : 
		return (cod[p],p+1)[self.ds.pop()]

	def rJz  (self,cod,p) : 
		return (p+1,cod[p])[self.ds.pop()==0]

	def rRun (dummy,self,cod,p) : 
		try:
			execute(self.rDict[cod[p]])
		except :
			print "[error] - Invalid command run-time error"
		return p+1

	def rPush(dummy,self,cod,p) : 
		#print "dummy-",dummy
		#print "self-",self
		#print "cod-",cod
		#print "p-",p
		self.ds.append(cod[p])     
		return p+1

	def rCreate (pcode,p) :
	    global lastCreate
	    lastCreate = label = getWord()      # match next word (input) to next heap address
	    self.rDict[label] = [rPush, self.heapNext]    # when created word is run, pushes its address

	def rDoes (self,cod,p) :
	    self.rDict[lastCreate] += cod[p:]        # rest of words belong to created words runtime
	    return len(cod)                     # jump p over these

	def rAllot (self,cod,p) :
	    self.heapNext += self.ds.pop()                # reserve n words for last create
	    return

	def rAt (self,cod,p) : 
		self.ds.append(self.heap[self.ds.pop()])       # get heap @ address
		return

	def rBang(self,cod,p) : 
		a=self.ds.pop()
		self.heap[a] = self.ds.pop()  		# set heap @ address
		return

	def rComa(self,cod,p) :                      # push tos into heap
	    self.heap[self.heapNext]=self.ds.pop()
	    self.heapNext += 1
	    return
	#================================= Zeitcoin Extention
	def rHelp(self,cod,p):
		print "=====================================Commands======================================="
		print "and - logic and operation (ie - true and true = true)"
		print "or  - logic or operation (ie - true and false = true)"
		print "max - Given two integers it will show the highest number"
		print "min - Given two integers it will show the lowest number"
		print "less - If the first number is less than the second than 1 is return else it returns 0"
		print "greater - If the first number is greater than the second than 1 else 0"
		print "ripemd160 - Returns the ripemd160 hash"
		print "hash160 - Returns the hash160 hash"
		print "hash256 - Returns the hash256 hash"
		print "sha1 - Returns the sha1 hash"
		print "sha256 - Returns the sha256 hash"
		print "verify - If one is pop from the stack than true is return else false"
		print "nip - Removes the second from the top of the stack"
		print "true - pops a 1 onto the top of the stack"
		print "false - pops a 0 onto the top of the stack"
		print "pick - ppo an element in the stack and put it on the top of the stack"
		print "roll - Duplicate an element in the stack and put it on the stack"
		print "num - Returns the length of the first element of the stack"
		print "len - Returns the number of elements on the stack"
		print "check - check the first element of the stack is signed correctly"
		print "swap - Swap the postion of the first two elements on the stack"
		print "dup - Duplicates the top element and push it onto the stack"
		print "drop - delete the first element of the stack"
		print "dump - dumps the stack to the screen"
		print "over - Duplicate the second element of the stack and push it onto the stack"
		print " + - Adds the first two elements of the stack together"
		print " - - Subtract the first two elements of the stack"
		print " * - Muliple the first two elements of the stack"
		print " / - Divide the first two elements of the stack"
		print " > - Returns true if the first number is greater than the second else false"
		print " < - Returns true if the first number is less than the second else false"
		print " = - If the first two elements are equal returns true else false"
		print " . - Tells that it is the end of the command-line"
		print "===================================================================================="
		return

	def rAnd(self,cod,p): 
		b=self.ds.pop()
		a=self.ds.pop()
		self.ds.append(a and b)
		return

	def rOr(self,cod,p): 
		b=self.ds.pop()
		a=self.ds.pop()
		self.ds.append(a or b)
		return

	def rMin(self,cod,p): 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			if (a>b):
				self.ds.append(b)
			else:
				self.ds.append(a)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)	
		return

	def rMax(self,cod,p):
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			if (a<b):
				self.ds.append(b)
			else:
				self.ds.append(a)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)	
		return

	def rLess(self,cod,p): 
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			if (a<b):
				self.ds.append(1)
			else:
				self.ds.append(0)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)	
		return

	def rGreater(self,cod,p):
		b=self.ds.pop()
		a=self.ds.pop()
		resulta=isinstance( a, ( int, long ) )
		resultb=isinstance( b, ( int, long ) )
		if (resulta and resultb):
			if (a>b):
				self.ds.append(1)
			else:
				self.ds.append(0)
		else:
			print "[error] - Can not use a string with this command"
			self.ds.append(0)
		return

	def rSha224(self,cod,p):
		a=str(self.ds.pop())
		a=self.stripstr(a)
		hashvalue=hashlib.sha224(a).hexdigest()
		self.ds.append(hashvalue)
		return 

	def rSha1(self,cod,p):
		a=str(self.ds.pop())
		a=self.stripstr(a)
		hashvalue=hashlib.sha1(a).hexdigest()
		self.ds.append(hashvalue)
		return

	def rSha256(self,cod,p):
		a=str(self.ds.pop())
		a=self.stripstr(a)
		hashvalue=hashlib.sha256(a).hexdigest()
		self.ds.append(hashvalue)
		return

	def rMd5(self,cod,p):
		a=str(self.ds.pop())
		a=self.stripstr(a)
		hashvalue=hashlib.md5(a).hexdigest()
		self.ds.append(hashvalue)
		return

	def rSha512(self,cod,p):
		a=str(self.ds.pop())
		a=self.stripstr(a)
		hashvalue=hashlib.sha512(a).hexdigest()
		self.ds.append(hashvalue)
		return

	def rVerify(self,cod,p):
		flag=1
		a=self.ds.pop()
		if (a!=1):
			self.ds.append(0)
			flag=0
		return flag

	def rTrue(self,cod,p):
		self.ds.append(1)
		return

	def rFalse(self,cod,p):
		self.ds.append(0)
		return

	def rNip(self,cod,p):
		a=self.ds.pop()
		b=self.ds.pop()
		self.ds.append(a)
		return

	def rNum(self,cod,p):
		l=len(ds)+1
		self.ds.append(l)
		return

	def rPick(self,cod,p):
		l=len(ds)
		a=self.ds.pop()
		result=isinstance( a, ( int, long ) )
		if (result==False):
			self.ds.append(0)
		else:
			a=int(a)-1
			if (a>l):
				self.ds.append(0)
			else:
				b=self.ds[a]
				self.ds.append(b)
		return

	def rRoll(self,cod,p):
		l=len(ds)
		a=self.ds.pop()
		result=isinstance( a, ( int, long ) )
		if (result==False):
			self.ds.append(0)
		else:
			a=int(a)-1
			if (a>l):
				self.ds.append(0)
			else:
				b=self.ds.pop(a)
				self.ds.append(b)
		return

	def rLen(self,cod,p):
		a=str(self.ds.pop())
		l=len(a)
		fletter = a[0]
		lletter = a[-1]
		if (fletter=='"' and lletter=='"'):
			l=l-2
		self.ds.append(l)
		return

	def rCheck(self,cod,p):
		b=self.ds.pop()  # signature
		a=self.ds.pop()  # message
		PubKey = M2Crypto.RSA.load_pub_key (PUBKEY)
		VerifyEVP = M2Crypto.EVP.PKey()
		VerifyEVP.assign_rsa (PubKey)
		VerifyEVP.verify_init ()
		VerifyEVP.verify_update (a)
		if VerifyEVP.verify_final (b) == 1:
	 		print "The string was successfully verified."
			verify = True
			self.ds.append(1)
		else:
	 		print "The string was NOT verified!"
			verify = False
			self.ds.append(0)
		return verify

	rDict = {
	  '+'  : rAdd, '-'   : rSub, '/' : rDiv, '*'    : rMul,   'over': rOver,
	  'dup': rDup, 'swap': rSwap, '.': rDot, 'dump' : rDump,  'drop': rDrop,
	  '='  : rEq,  '>'   : rGt,   '<': rLt,
	  ','  : rComa,'@'   : rAt, '!'  : rBang,'allot': rAllot,
	  'and': rAnd, 'or'  : rOr, 'min': rMin, 'max'  : rMax,  'len'  :rLen,
	  'create': rCreate, 'does>': rDoes, 'check' : rCheck, 'num'  : rNum,
	  'roll'  : rRoll,   'pick' : rPick, 'nip'   : rNip,   'true' : rTrue,
	  'false' : rFalse,  'verify' : rVerify, 'md5' : rMd5,
	  'sha512' : rSha512, 'sha1' : rSha1,  'sha256'  : rSha256, 
	  'sha224' : rSha224, 'less' : rLess, 'greater' : rGreater, 'help' : rHelp,  
	}

	#================================= Compile time 

	def compile(self,word) :
		pcode = []; 
		#word = getWord(prompt)  # get next word
		if word == None : return None
		cAct = self.cDict.get(word)  # Is there a compile time action ?
		rAct = self.rDict.get(word)  # Is there a runtime action ?

		if cAct : cAct(pcode)   # run at compile time
		elif rAct :
		    if type(rAct) == type([]) :
		        pcode.append(self.rRun)     # Compiled word.
		        pcode.append(word)     # for now do dynamic lookup
		    else : pcode.append(rAct)  # push builtin for runtime
		else :
		    # Number to be pushed onto ds at runtime
		    pcode.append(self.rPush)
		    try : pcode.append(int(word))
		    except :
		        try: pcode.append(float(word))
		        except : 
			    fletter = word[0]
			    lletter = word[-1]
			    if (fletter=='"' and lletter=='"'):
				pcode.append(str(word))
			    else:
		            	pcode[-1] = self.rRun     # Change rPush to rRun
		            	pcode.append(word)   # Assume word will be defined
		return pcode    
	    
	def fatal (mesg) : raise mesg

	def cColon (pcode) :
	    if self.cStack : fatal(": inside Control stack: %s" % self.cStack)
	    label = getWord()
	    self.cStack.append(("COLON",label))  # flag for following ";"

	def cSemi (pcode) :
	    if not self.cStack : fatal("No : for ; to match")
	    code,label = self.cStack.pop()
	    if code != "COLON" : fatal(": not balanced with ;")
	    self.rDict[label] = pcode[:]       # Save word definition in rDict
	    while pcode : pcode.pop()

	def cBegin (pcode) :
	    self.cStack.append(("BEGIN",len(pcode)))  # flag for following UNTIL

	def cUntil (pcode) :
	    if not self.cStack : fatal("No BEGIN for UNTIL to match")
	    code,slot = self.cStack.pop()
	    if code != "BEGIN" : fatal("UNTIL preceded by %s (not BEGIN)" % code)
	    pcode.append(rJz)
	    pcode.append(slot)

	def cIf (pcode) :
	    pcode.append(rJz)
	    self.cStack.append(("IF",len(pcode)))  # flag for following Then or Else
	    pcode.append(0)                   # slot to be filled in

	def cElse (pcode) :
	    if not self.cStack : fatal("No IF for ELSE to match")
	    code,slot = self.cStack.pop()
	    if code != "IF" : fatal("ELSE preceded by %s (not IF)" % code)
	    pcode.append(rJmp)
	    self.cStack.append(("ELSE",len(pcode)))  # flag for following THEN
	    pcode.append(0)                     # slot to be filled in
	    pcode[slot] = len(pcode)            # close JZ for IF

	def cThen (pcode) :
	    if not self.cStack : fatal("No IF or ELSE for THEN to match")
	    code,slot = self.cStack.pop()
	    if code not in ("IF","ELSE") : fatal("THEN preceded by %s (not IF or ELSE)" % code)
	    pcode[slot] = len(pcode)             # close JZ for IF or JMP for ELSE

	cDict = {
	  ':'    : cColon, ';'    : cSemi, 'if': cIf, 'else': cElse, 'then': cThen,
	  'begin': cBegin, 'until': cUntil,
	}

	def run(self,script) :
	    self.tokenizeWords(script)
	    for word in self.words:
		pcode = self.compile(word)          # compile/run from user
		if pcode == None : print; return
		self.execute(pcode)
	    result = self.ds.pop()
	    print "result-",result
	    return result

def main():
	zf=zeitforth()
	script = raw_input("Enter the forth code to be run\n")
	zf.run(script)
  
if __name__ == "__main__" : main()

