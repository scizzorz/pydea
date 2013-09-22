import os
import time
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
						val = temp.group(2)
						if val.lower() == 'true':
							val = True
						elif val.lower() == 'false':
							val = False
						elif val.isdigit():
							val = int(val)
						elif temp.group(1) == 'tags':
							val = val.split(' ')
							val.sort()

						self[temp.group(1)] = val
					else:
						metamode = 'read'

				if metamode == 'read':
					self._source += line

		self._source = self._source.strip()

	def _process(self):
		if 'datetime' in self:
			timestamp = time.strptime(self['datetime'], FMT_DATETIME)
			self.timestamp = time.mktime(timestamp)

	def __eq(self, other):
		return self.timestamp == other.timestamp
	def __ne__(self, other):
		return self.timestamp != other.timestamp
	def __le__(self, other):
		return self.timestamp <= other.timestamp
	def __lt__(self, other):
		return self.timestamp < other.timestamp
	def __ge__(self, other):
		return self.timestamp >= other.timestamp
	def __gt__(self, other):
		return self.timestamp > other.timestamp

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
	idea_files = []
	def __init__(self, path):
		self.path = os.path.basename(os.path.dirname(path))
		self.basename = os.path.basename(path)

		if not os.path.exists(path):
			return
		if not os.path.isdir(path):
			return

		for filename in sorted(os.listdir(path)):
			full_path = os.path.join(path, filename)

			if filename == 'meta.md':
				self.exists = True
				self._parse(full_path)
				self._process()
				self.metafile = full_path
				continue

			if filename.endswith('.md') and full_path not in self.idea_files:
				self.idea_files.append(full_path)
				self.ideas.append(Idea(full_path))

		self.ideas.sort()

	def __repr__(self):
		return '# {}\n\n{}'.format(self['title'], self.render())

	def render(self, output = 'text'):
		if output == 'html':
			return '<hr style="width:20em; margin: 1em auto; border-width: 0 0 2px 0; border-style: dotted">\n'.join(str(x) for x in self.ideas)

		return '\n'.join('* '+str(x) for x in self.ideas)

class Idea(Meta):
	'''A container for a single Pydea file and its metadata.'''
	def __init__(self, filename):
		self._name = os.path.splitext(filename)[0]
		self._parse(filename)
		self._process()

	def __repr__(self):
		return self._source
