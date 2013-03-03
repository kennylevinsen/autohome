#!/usr/bin/python2.7
from __future__ import print_function, absolute_import
from time import mktime, time, sleep
from threading import Thread
from json import loads
from dateutil.rrule import rrule, DAILY
from serial import Serial
from SocketServer import BaseRequestHandler, TCPServer
from socket import timeout
from sys import argv
from automated import Automated, AutoSartano

serfile = argv[1]
eventFile = argv[2]
listenPort = int(argv[3])

ser = Serial(serfile, 9600, timeout=1)

def switcher(id, state):
   ser.write(chr(state<<7|id))

automators = {
	'A': AutoSartano(3, switcher),
	'B': AutoSartano(2, switcher),
	'C': AutoSartano(1, switcher),
	'D': AutoSartano(0, switcher),
	'EXT': AutoSartano(127, switcher)
}

def allOff():
	for i in automators:
		i.off()

class eventScheduler(Thread):
	def run(self):
		self.internalList = []
		self.reloadEvents()

		while True:
			next = self.handleEvents()
			if next < 60:
				sleep(next)
			else:
				sleep(60)

	def reloadEvents(self):
		with open(eventFile) as f:
			self.events = loads(f.read())
		self.internalList = []

		for el in self.events:
			print('New event:', el)
			self.internalList.append(self.createEvent(el))

	def createEvent(self, event):
		return { "event": event,
					"timestamp": mktime(rrule(DAILY, count=1, byhour=event['time']['hours'], byminute=event['time']['minutes'], bysecond=0)[0].timetuple())}

	def handleEvents(self):
		tmp = self.internalList
		cur = time()
		next = 0
		for idx, event in enumerate(tmp):
			t = event['timestamp'] - cur
			if t <= 0:
				print('Executing', event['event']['name'])
				for el in event['event']['actions']:
					automators[event['id']].set_state(el['state'])
				self.internalList[idx] = self.createEvent(event['event'])
			elif t > next:
				next = t
		return next+1

scheduler = eventScheduler()
scheduler.daemon = True
scheduler.start()

commands = {
	"A_ON": lambda: automators['A'].on(),
	"B_ON": lambda: automators['B'].on(),
	"C_ON": lambda: automators['C'].on(),
	"D_ON": lambda: automators['D'].on(),
	"EXT_ON": lambda: automators['EXT'].on(),
	"A_OFF": lambda: automators['A'].off(),
	"B_OFF": lambda: automators['B'].off(),
	"C_OFF": lambda: automators['C'].off(),
	"D_OFF": lambda: automators['D'].off(),
	"EXT_OFF": lambda: automators['EXT'].off(),
	"ALL_OFF": lambda: allOff()
}

class TCPHandler(BaseRequestHandler):
	def parseData(self, data):
		parts = data.split(':')

		setOptions = []
		returnString = ""

		for element in parts:
			subparts = element.split('=')
			if len(subparts) == 2:
				options[subparts[0]] = subparts[1]
				if subparts[0] not in setOptions:
					setOptions.append(subparts[0])

		parts[0] = parts[0].upper()
		if parts[0] in commands:
			returnString = commands[parts[0]]()
		else:
			returnString = "INVALID"

		if not returnString:
			returnString = "OK"

		for i in setOptions:
			returnString += ":" + i + "=" + options[i]
		return returnString + "\n"

	def handle(self):
		self.request.settimeout(1)
		print("Connection from " + self.client_address[0])
		try:
			self.data = self.request.recv(1024).strip()
			print ("{} wrote:".format(self.client_address[0]))
			print (self.data)
			self.request.sendall(self.parseData(self.data))
		except timeout:
			self.request.sendall("TIMEOUT\n")

	def finish(self):
		print("Connection closed")

TCPServer.allow_reuse_address = True
server = TCPServer(('0.0.0.0', listenPort), TCPHandler)

server.serve_forever()
