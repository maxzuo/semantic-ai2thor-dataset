from . import metadata
from .loaders import *

def reconnect():
  """
  Attempt to reconnect global connection to AI2Thor database
  """
  from .globals import connect
  connect()
