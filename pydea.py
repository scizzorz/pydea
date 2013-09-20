#!/usr/bin/env python
import bumpy
import os
import re
import sys
import tempfile
import time

RE_META = re.compile(r'^\* (\w+)\s*=\s*(.*)$')
FMT_DATETIME = '%m/%d/%Y %I:%M%p'

CONFIG = {
	'path': '.pydea',
	'editor': os.getenv('EDITOR', 'nano'),
	}

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
		self.path = path
		if not os.path.exists(path):
			return
		if not os.path.isdir(path):
			return

		for filename in sorted(os.listdir(path)):
			full_path = os.path.join(path, filename)

			if filename == 'meta.md':
				self.exists = True
				self._parse(full_path)
				self.metafile = full_path
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

@bumpy.private
@bumpy.setup
def setup():
	global stream
	stream = Stream(CONFIG['path'])

@bumpy.private
@bumpy.options
def options(**kwargs):
	for key in kwargs:
		CONFIG[key] = kwargs[key]

@bumpy.args(title='Untitled', tags='none')
def init(**kwargs):
	'''Initialize a Pydea stream.'''
	if stream.exists: bumpy.abort('Already a Pydea stream')

	if not os.path.exists(stream.path):
		os.makedirs(stream.path)

	with open(os.path.join(stream.path, 'meta.md'), 'w+') as temp:
		temp.write('* title = {}\n'.format(kwargs['title']))
		temp.write('* tags = {}\n'.format(kwargs['tags']))

	print 'Created empty Pydea stream'

@bumpy.alias('view', 'list')
def show():
	'''View the Pydea stream.'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	print stream

@bumpy.task
def edit():
	'''Edit the Pydea metadata.'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')
	os.system('{} "{}"'.format(CONFIG['editor'], stream.metafile))

@bumpy.default
def add(*args):
	'''Add a new Pydea.'''
	if not stream.exists: bumpy.abort('Not a Pydea stream')

	now = str(int(time.time()))
	datetime = time.strftime(FMT_DATETIME, time.localtime())
	full_path = os.path.join(stream.path, now + '.md')

	if args: # has arguments
		contents = '\n\n'.join(args).strip()

	else: # no arguments, open $EDITOR
		desc, name = tempfile.mkstemp(suffix='.md', text = True)
		os.system('{} "{}"'.format(CONFIG['editor'], name))

		with open(name) as arg:
			contents = arg.read().strip()

	with open(full_path, 'w+') as temp:
		temp.write('* datetime = {}\n\n'.format(datetime))
		if contents:
			temp.write(contents)
			print 'Added Pydea ' + now
		else:
			bumpy.abort('Pydea contents were empty')

if __name__ == '__main__':
	suppress = [key for key in bumpy.LOCALE if not key.startswith('abort')]

	bumpy.config(cli = True)
	bumpy.config(suppress = suppress)
	bumpy.config(long_options=[x+'=' for x in CONFIG])
	bumpy.main(sys.argv[1:])
