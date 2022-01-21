#!/bin/python3
# Copyright 2022, Max Brueggemann, www.maxbrueggemann.de
# This program searches the current directory for python files
# that have a filename beginning with "rRun". These files are then
# executed as subprocesses. The subprocesses will be terminated when
# the corresponding file has vanished. Has a file has been modified,
# the subprocess will be restarted.

import os
import subprocess
import sys
import multiprocessing
import time
import signal
import sys


class Rule:
	def __init__(self,filename):
		self.filename=filename
		self.fileExists=True
		try:
			self.time=os.path.getmtime(self.filename)
		except:
			self.time=0
		self.subprocess=None
		print("Found script "+filename)
		self.start()

	def kill(self):
		print("Killing script "+self.filename)
		self.subprocess.kill()

	def start(self):
		print("Starting script "+self.filename)
		self.subprocess = subprocess.Popen([sys.executable, self.filename])

	def modified(self):
		time=self.time
		try:
			time=os.path.getmtime(self.filename)
		except:
			pass
		if self.time != time:
			self.time=time
			print(self.filename+" changed. Reloading.")
			self.kill()
			self.start()

scriptList=[]

def signal_handler(signal, frame):
	for x in scriptList:
		x.kill()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
	fileList=os.listdir(".")
	for x in scriptList:
		x.fileExists=False

	for x in fileList:
		found = False
		if x.startswith("rRun") and x.endswith(".py"):
			for y in scriptList:
				if y.filename == x:
					y.fileExists=True
					found=True
			if not found:
				scriptList.append(Rule(x))	

	time.sleep(3)
	for x in scriptList:
		x.modified()
		if not x.fileExists:
			print("Script "+x.filename+" is gone.")
			x.kill()
			scriptList.remove(x)


