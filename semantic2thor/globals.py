import sqlite3
import os

try:
  from tqdm import tqdm
except ImportError:
  tqdm = lambda x, **a: x

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ai2thor.db')
CONN = None

def connect():
  global CONN
  if CONN is not None:
    try:
      CONN.close()
    except:
      pass
  CONN = sqlite3.connect(DB_PATH)

connect()