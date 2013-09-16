#!/usr/bin/env python
import bumpy
import os
import re
import sys
import tempfile
import time

RE_META = re.compile(r'^\* (\w+)\s*=\s*(.*)$')
FMT_DATETIME = '%m/%d/%Y %I:%M%p'

class Stream:
	def __init__(self):
		if not os.path.exists('.pydea'):
			self.exists = False
			return

		self.exists = True
		self.ideas = [Idea(f) for f in sorted(os.listdir('.'))
			if f.endswith('.pydea.md')]

class Idea:
	def __init__(self, filename):
		self._name = os.path.splitext(filename)[0]
		self._source = ''
		self._metas = dict()
		self._parse(filename)

	def _parse(self, filename):
		metamode = 'meta'
		with open(filename) as source:
			for line in source:
				if metamode == 'meta':
					temp = RE_META.match(line)
					if temp:
						self._metas[temp.group(1)] = temp.group(2)
					else:
						metamode = 'read'

				if metamode == 'read':
					self._source += line

		self._source = self._source.strip()

	def __repr__(self):
		return '* {}'.format(self._source)

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

	for idea in stream.ideas:
		print idea

@bumpy.default
def add(*args):
	'''Add a new Pydea'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	now = str(int(time.time()))
	with open(now + '.pydea.md', 'w+') as temp:
		datetime = time.strftime(FMT_DATETIME, time.localtime())
		temp.write('* datetime = {}\n\n'.format(datetime))
		if args:
			for arg in args:
				temp.write(arg + '\n\n')

		else:
			desc, name = tempfile.mkstemp(prefix = 'pydea-', suffix='.md', text = True)
			os.system('{} "{}"'.format(os.getenv('EDITOR', 'nano'), name))

			with open(name) as arg:
				temp.write(arg.read().strip())

	print 'Added Pydea ' + now

@bumpy.setup
@bumpy.private
def setup():
	global stream
	stream = Stream()

if __name__ == '__main__':
	suppress = [key for key in bumpy.LOCALE if not key.startswith('abort')]
	bumpy.config(cli = True, suppress = suppress)
	bumpy.main(sys.argv[1:])
