from __future__ import unicode_literals, absolute_import, division, print_function
from .bucket_core import *
from .bucket_sql import *
from .bucket_factoid import *
from .bucket_inventory import *
from .bucket_nicktracker import *
from .bucket_gender import *
def setup(sopel):
    bucket_sql.setup(sopel)
