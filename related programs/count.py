#!/usr/bin/python
############################################################
# Count Class - Use to count the length of certain objects
############################################################

import sys, os
from PIL import Image

class count:

	def wordcount(self, str1):
		# count the number of words in a string
		wc=len(str1.split(" "))
		return wc

	def bytecount(self, file1):
		# count the number of bytes in a file
		bc=os.stat(file1).st_size
		return bc

	def pixelcount(self, img1):
		# count the number of pixel in an image
		img = Image.open(img1)
		width, height = img.size
		return width * height


def main():
	c=count()
	print "Testing the count class"
	str1="this is a test sentence"
	wc=c.wordcount(str1)
	bc=c.bytecount("test.txt")
	img1=c.pixelcount("testimage.jpg")
	print str1+"- has "+str(wc)+" words"
	print "The file test.txt has "+str(bc)+" bytes"
	print "The image testimage.jpg has "+str(img1)+" pixels"
	print "Test for count class is finish"
	exit(0)

if __name__ == '__main__':
    main()
