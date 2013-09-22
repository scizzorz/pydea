import os
import re

RE_META = re.compile(r'^\* (\w+)\s*=\s*(.*)$')
FMT_DATETIME = '%m/%d/%Y %I:%M%p'

CONFIG = {
	'path': '.pydea',
	'editor': os.getenv('EDITOR', 'nano'),
	}

CONFIG_SHORTS = {
	'p': 'path',
	'e': 'editor',
	}
