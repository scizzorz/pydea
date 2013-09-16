#!/usr/bin/env python
import bumpy
import os
import re
import sys
import tempfile
import time

RE_META = re.compile(r'^\* (\w+)\s*=\s*(.*)$')
FMT_DATETIME = '%m/%d/%Y %I:%M%p'
EDITOR = os.getenv('EDITOR', 'nano')

class Meta:
	'''An interface for loading a file and processing metadata encoded in a
	   Markdown list at the top of the file.'''
	_metas = {}
	_source = ''
	def _parse(self, filename):
		metamode = 'meta'
		with open(filename) as source:
			for line in source:
				if metamode == 'meta':
					temp = RE_META.match(line)
					if temp:
						self[temp.group(1)] = temp.group(2)
					else:
						metamode = 'read'

				if metamode == 'read':
					self._source += line

		self._source = self._source.strip()

	def __len__(self):
		return len(self._metas)

	def __getitem__(self, key):
		return self._metas[key]

	def __setitem__(self, key, value):
		self._metas[key] = value

	def __delitem__(self, key):
		del self._metas[key]

	def __contains__(self, item):
		return item in self._metas

class Stream(Meta):
	'''A container for general metadata about a Pydea stream as well as a list of
	   Pydea files in the stream.'''
	exists = False
	ideas = []
	def __init__(self, path):
		if not os.path.exists(path):
			return

		for filename in sorted(os.listdir(path)):
			full_path = os.path.join(path, filename)

			if filename == 'meta.md':
				self.exists = True
				self._parse(full_path)
				self.metafile = full_path
				self.path = path
				continue

			self.ideas.append(Idea(full_path))

	def __repr__(self):
		return '# {}\n\n{}'.format(self['title'], '\n'.join(str(x) for x in self.ideas))

class Idea(Meta):
	'''A container for a single Pydea file and its metadata.'''
	def __init__(self, filename):
		self._name = os.path.splitext(filename)[0]
		self._parse(filename)

	def __repr__(self):
		return '* {}'.format(self._source)

@bumpy.task
def init():
	'''Initialize a Pydea stream.'''
	if stream.exists: bumpy.abort('Already a Pydea stream')

	with open('.pydea', 'w+') as temp:
		temp.write('* title = Untitled\n')
		temp.write('* tags = none\n')

	print 'Created empty Pydea stream'

@bumpy.task
def show():
	'''View the Pydea stream.'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	print stream

@bumpy.default
def add(*args):
	'''Add a new Pydea.'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	now = str(int(time.time()))
	with open(now + '.pydea.md', 'w+') as temp:
		datetime = time.strftime(FMT_DATETIME, time.localtime())
		temp.write('* datetime = {}\n\n'.format(datetime))
		if args:
			for arg in args:
				temp.write(arg + '\n\n')

		else:
			desc, name = tempfile.mkstemp(suffix='.md', text = True)
			os.system('{} "{}"'.format(EDITOR, name))

			with open(name) as arg:
				contents = arg.read().strip()
				temp.write(arg.read().strip())

				if contents:
					print 'Added Pydea ' + now
				else:
					bumpy.abort('Pydea file was empty')

@bumpy.setup
@bumpy.private
def setup():
	global stream
	stream = Stream('.pydea')

if __name__ == '__main__':
	suppress = [key for key in bumpy.LOCALE if not key.startswith('abort')]
	bumpy.config(cli = True, suppress = suppress)
	bumpy.main(sys.argv[1:])
