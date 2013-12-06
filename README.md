zeitcoin
========

Zeitcoin is a new digital-currency that is like bitcoin but address some issue that the other digital-currency has.  For example, it is immune to the 51% attack.  Furthermore, it allows people to earn digital coins by not just mining but also by contributing software, music, video, writing, and drawings. (Please note, this is not a finish project yet but will be soon)

For those that want to help with this project
=============================================

This program is written using python and uses the twisted framework.  For those who are not familiar with the twisted framework or has written asynchronous type of programs will have a little bit of a learning curve but once you get familiar with this style of programming it will become second nature. Also, it uses WxPython for the graphical user interface such as the wallet. It is a decentalized peer to peer program that uses a distributed hast table to track peers.  It uses a modified versus of the kamilla protocol. This program uses the AMP protocol to communicate between the peers on the network.  Also, it uses the JSON-RPC protocol to allow users to externally communicate with a wallet.  This digital-currency uses the Guided Tour Puzzle protocol (see the guidedtour.pdf for a description of this protocol) to perform the proof-of-work to prevent double spending.  Some useful files that one can look at to get familiar with the program design. The file "structure.txt" describe the different files used by this program and how the program is structured.  The file "database.txt" describe the structure of the database used by this program (SQLLite).  The file "protocol.doc" describe the two main protocol used by this program to communicate (AMP and JSON-RPC) and gives a references for the commands used by the network. The file "transactionsscripting.doc" describe the forth like scripting language used for verifying transaction. I will add more technical documents that describe the operation of this program in more detail as time permits. 

Testing
=======
There are two files that I have designed to help you test the functionality of the network.  Zeitnetwork.py is a command-line testing program and Zeitnetgui.py is the GUI version.  Just start the program, enter the number of peers in the testing network and the starting port of the first peer.  They will create a sub-process that represent each peer on the network and then you can send and receive commands from the different peers. 

Things to do
============
I will give a list of things that need to be done below:
* The file zeitcoindb.py holds the class that does all the database function.  I need this file to be check for SQL-Injection issues
* Need to run the testing programs and walk through each command and make sure the commands are working correctly.
* Need to test out the forth like scripting language used to verify transaction and make sure the scripting language is working correctly.

* Note: I will add more to this to do list when I have more time
