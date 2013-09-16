#!/usr/bin/env python
import os
import sys

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

def main(args):
	stream = Stream()
	if len(args) == 1:
		if args[0] == 'init':
			if stream.exists:
				print 'Already a pydea stream'
				return

			with open('.pydea', 'w+') as temp:
				temp.write('* title = Testing\n')
			print 'Created empty pydea stream'
		elif args[0] == 'view':
			if not stream.exists:
				print 'Not a pydea stream'
				return

			print 'Finding pydeas...'
	else:
		if not stream.exists:
			print 'Not a pydea stream'
			return

		print 'Adding pydea...'

if __name__ == '__main__':
	main(sys.argv[1:])
