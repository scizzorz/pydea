import os
from .globals import *

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

			if filename.endswith('.md'):
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
