import bumpy
import sys
from .globals import *
from .tasks import *

suppress = [key for key in bumpy.LOCALE if not key.startswith('abort')]

bumpy.config(cli = True)
bumpy.config(suppress = suppress)
bumpy.config(options=''.join([x+':' for x in CONFIG_SHORTS]))
bumpy.config(long_options=[x+'=' for x in CONFIG])
bumpy.main(sys.argv[1:])
