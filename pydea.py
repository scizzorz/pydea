#!/usr/bin/env python
import bumpy
import os
import sys
import time

FMT_DATETIME = '%m/%d/%Y %I:%M%p'

class Stream:
	def __init__(self):
		if not os.path.exists('.pydea'):
			self.exists = False
			return

		self.exists = True
		self.ideas = [Idea(f) for f in sorted(os.listdir('.'))
			if os.path.splitext(f)[1] == '.md']

class Idea:
	def __init__(self, filename):
		self.name = os.path.splitext(filename)[0]
		self.source = open(filename).read()

	def __repr__(self):
		return '[Idea: {}]'.format(self.name)

@bumpy.task
def init():
	'''Initialize a Pydea stream'''
	if stream.exists: bumpy.abort('Already a Pydea stream')

	with open('.pydea', 'w+') as temp:
		temp.write('* title = Testing\n')
	print 'Created empty Pydea stream'

@bumpy.task
def show():
	'''View the Pydea stream'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	print stream.ideas

@bumpy.task
def add(*args):
	'''Add a new Pydea'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	now = str(int(time.time()))
	with open(now + '.md', 'w+') as temp:
		datetime = time.strftime(FMT_DATETIME, time.localtime())
		temp.write('* datetime = {}\n\n'.format(datetime))
		for arg in args:
			temp.write(arg + '\n\n')

	print 'Added Pydea ' + now

@bumpy.default
@bumpy.private
def default(*args):
	'''Add items to the Pydea stream or display it'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	if args:
		add(*args)
	else:
		show()

@bumpy.setup
@bumpy.private
def setup():
	global stream
	stream = Stream()

if __name__ == '__main__':
	suppress = [key for key in bumpy.LOCALE if not key.startswith('abort')]
	bumpy.config(cli = True, suppress = suppress)
	bumpy.main(sys.argv[1:])
