import bumpy
import os
import sys
import tempfile
import time
from .globals import *
from .classes import *

@bumpy.private
@bumpy.setup
def setup():
	global stream
	stream = Stream(CONFIG['path'])

@bumpy.private
@bumpy.options
def options(**kwargs):
	for key in kwargs:
		if key in CONFIG_SHORTS:
			ckey = CONFIG_SHORTS[key]
		else:
			ckey = key

		CONFIG[ckey] = kwargs[key]

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
