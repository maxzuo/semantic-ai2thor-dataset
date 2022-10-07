import sqlite3
import json
import csv
from ast import literal_eval

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

import tqdm

with open('init_database.sql', 'r') as f:
  CREATE_TABLES = f.read()

ai2thor_data = dict()
with open('ai2thor_affordances.csv', 'r', newline='') as f:
  csv_reader = csv.reader(f)
  # AFFORDANCES = set()
  ROBOCSE = set()
  next(csv_reader)
  for name, wordnet_name, flag, ai2thor_robocse, _ in csv_reader:
    # AFFORDANCES.update(literal_eval(affordances))
    if ai2thor_robocse is not None and ai2thor_robocse != 'None':
      ROBOCSE.update(literal_eval(ai2thor_robocse))
    ai2thor_data[name] = dict(wordnet=wordnet_name, robocse=literal_eval(ai2thor_robocse))


# AFFORDANCES = sorted(AFFORDANCES)
ROBOCSE = sorted(ROBOCSE)
DB_PATH = './ai2thor-lite.db'
CONN = None

def build_db():
  print('Creating tables...')
  commands = CREATE_TABLES.split(';')
  for cmd in tqdm.tqdm(commands):
    # print(cmd)
    CONN.execute(cmd)

  CONN.commit()

def build_walmart_graph(objects):
  print('Creating walmart graph...')
  created_nodes = set()
  for object in tqdm.tqdm(objects):
    for p in object['path']:
      path = ['Object', *p]
      for i in range(1,len(path)):
        node = path[i]
        if node in created_nodes:
          continue
        CONN.execute('INSERT INTO walmart (node, parent) VALUES (?, ?)', (node, path[i-1]))
        created_nodes.add(node)

  CONN.commit()

def add_conceptnet(objects):
  print('Adding conceptnet embeddings...')
  required = set([o['Conceptnet Name'].lower().strip() for o in objects])
  embeddings = []
  with open('numberbatch-en-19.08.txt', 'r', encoding='utf-8') as f:
    f.readline()
    for l in tqdm.tqdm(f):
      key, *emb = l.split()

      if key.lower().strip() in required:
        embeddings.append((key, np.asarray(emb, dtype=np.float32).tobytes()))

  CONN.executemany('INSERT INTO conceptnet VALUES (?, ?)', embeddings)
  CONN.commit()

def add_objects(objects):
  objects = [(o['Object Type'], o['Conceptnet Name'], ai2thor_data.get(o['Object Type'], {}).get('wordnet'),
              o['Contextual Interactions'] if o['Contextual Interactions'] != '' else None) for o in tqdm.tqdm(objects)]
  CONN.executemany('INSERT INTO objects VALUES (?, ?, ?, ?)', objects)
  CONN.commit()

def add_receptacle_relations(objects):
  print('Creating receptacle relations...')
  receptacles = [(o['Object Type'], r) for o in tqdm.tqdm(objects) for r in o['Default Compatible Receptacles']]
  CONN.executemany('INSERT OR IGNORE INTO receptacles VALUES (?, ?)', receptacles)
  CONN.commit()

def add_scene_relations(objects):
  print('Creating scene relations...')
  scenes = [(o['Object Type'], scene) for o in tqdm.tqdm(objects) for scene in o['Scenes']]
  CONN.executemany('INSERT INTO scenes VALUES (?, ?)', scenes)
  CONN.commit()

def add_material_relations(objects):
  print('Creating material relations...')
  materials = []
  for o in tqdm.tqdm(objects):
    for m in o['Material Properties']:
      m = m.split()
      m = m[len(m) // 2]
      materials.append((o['Object Type'], m))

  CONN.executemany('INSERT INTO material_properties VALUES (?, ?)', materials)
  CONN.commit()

def add_parent_relations(objects):
  print('Creating parent relations')
  parents = [(o['Object Type'], p[-1]) for o in tqdm.tqdm(objects) for p in o['path']]
  CONN.executemany('INSERT INTO object_parents VALUES (?, ?)', parents)
  CONN.commit()

def add_ai2thor_action_relations(objects):
  print('Creating ai2thor_action relations...')
  ai2thor_actions = [(o['Object Type'], a.replace(' (Some)', ''), ' (Some)' in a) for o in tqdm.tqdm(objects) for a in o['Actionable Properties']]
  CONN.executemany('INSERT INTO ai2thor_actions VALUES (?, ?, ?)', ai2thor_actions)
  CONN.commit()


class _PCA():
  '''
  Source: Max Zuo's homework for CS 4641 (Fall 2019)
  A popular feature transformation/reduction/visualization method


  Uses the singular value decomposition to find the orthogonal directions of
  maximum variance.
  '''
  def __init__(self):
    '''
    Initializes some data members to hold the three components of the
    SVD.
    '''
    self.u = None
    self.s = None
    self.v = None
    self.shift = None
    self.data = None

  def find_components(self,data):
    '''
    Finds the SVD factorization and stores the result.


    Args:
      data: A NxD array of data points in row-vector format.
    '''

    self.shift = np.mean(data, axis=0)
    self.data = data - self.shift

    self.u, self.s, self.v = np.linalg.svd(self.data, full_matrices=False)
    self.v = self.v.T

    #TODO: Your code here

  def transform(self,n_components,data=None):
    '''
    Uses the values computed and stored after calling find_components()
    to transform the data into n_components dimensions.


    Args:
      n_components: The number of dimensions to transform the data into.
      data:   the data to apply the transform to. Defaults to the data
          provided on the last call to find_components()


    Returns:
      transformed_data:   a Nx(n_components) array of transformed points,
                in row-vector format.
    '''
    if data is None:
      data = self.data

    self.find_components(self.data)
    #NOTE: Don't forget to center the data

    #TODO: Your code here
    centered = data - self.shift

    transformed = centered.dot(self.v[:,:n_components])

    return transformed

  def inv_transform(self,n_components,transformed_data):
    '''
    Inverts the results of transform() (if given the same arguments).


    Args:
      n_components:    Number of components to use. Should match
                the dimension of transformed_data.
      transformed_data:  The data to apply the inverse transform to,
                should be in row-vector format


    Returns:
      inv_tform_data:    a NxD array of points in row-vector format
    '''
    #NOTE: Don't forget to "un-center" the data
    # uncentered = transformed_data + self.shift

    inv = transformed_data.dot(self.v[:,:n_components].T)
    return inv + self.shift
    #TODO: Your code here

  def reconstruct(self,n_components,data=None):
    '''
    Casts the data down to n_components dimensions, and then reverses the transform,
    returning the low-rank approximation of the given data. Defaults to the data
    provided on the last call to find_components().
    '''
    return self.inv_transform(n_components,self.transform(n_components,data))

  def reconstruction_error(self,n_components,data=None):
    '''
    Useful for determining how much information is preserved in n_components dimensions.
    '''
    if data is None:
      data = self.data
    return np.linalg.norm(data-self.reconstruct(n_components,data),ord='fro')


def add_affordances():
  # print('Creating affordances table')
  # print(
  #   f'''CREATE TABLE affordances (
  #         object_type text NOT NULL,
  #         {", ".join(f"{affordance} bool" for affordance in AFFORDANCES)},
  #         PRIMARY KEY (object_type),
  #         FOREIGN KEY (object_type) REFERENCES objects(name)
  #       );''')
  # CONN.execute(f'''CREATE TABLE affordances (
  #         object_type text NOT NULL,
  #         {", ".join(f"{affordance} bool" for affordance in AFFORDANCES)},
  #         PRIMARY KEY (object_type),
  #         FOREIGN KEY (object_type) REFERENCES objects(name)
  #       );''')

  # print('Creating affordances')
  # object_affordances = [(name, *(a in o['affordances'] for a in AFFORDANCES)) for name, o in tqdm.tqdm(ai2thor_data.items())]
  # CONN.executemany(f'INSERT INTO affordances VALUES ({"?, " * len(AFFORDANCES)}?)', object_affordances)
  # CONN.commit()

  print('Creating RoboCSE table')
  print(f'''CREATE TABLE robocse (
          object_type text NOT NULL,
          {", ".join(f"{affordance} bool" for affordance in ROBOCSE)},
          PRIMARY KEY (object_type),
          FOREIGN KEY (object_type) REFERENCES objects(name)
        );''')
  CONN.execute(f'''CREATE TABLE robocse (
          object_type text NOT NULL,
          {", ".join(f"{affordance} bool" for affordance in ROBOCSE)},
          pca_embedding blob,
          PRIMARY KEY (object_type),
          FOREIGN KEY (object_type) REFERENCES objects(name)
        );''')
  CONN.commit()
  print('Creating robocse')
  object_robocse = [[name, *(a in (o['robocse'] if o['robocse'] is not None else set()) for a in ROBOCSE)] for name, o in tqdm.tqdm(ai2thor_data.items())]
  vector_cse = np.asarray([a for _, *a in object_robocse], dtype=np.float32)
  _pca = _PCA()
  _pca.find_components(vector_cse)
  error = [_pca.reconstruction_error(i) for i in range(25)]
  plt.plot(error, marker='o')
  plt.title('Reconstruction error')
  plt.xlabel('Number of components used for reconstruction')
  plt.ylabel('Error (Euclidean)')
  plt.tight_layout()
  plt.show()

  n_components = input('Number of dimensions to use in PCA (default MLE): ')
  n_components = int(n_components) if n_components else 'mle'

  pca = PCA(n_components=n_components)
  vector_cse = pca.fit_transform(vector_cse)
  for i, vector in enumerate(vector_cse):
    object_robocse[i].append(vector.tobytes())

  CONN.executemany(f'INSERT INTO robocse VALUES ({"?, " * len(ROBOCSE)}?, ?)', object_robocse)

  CONN.commit()

if __name__ == '__main__':
  CONN = sqlite3.connect(DB_PATH)
  build_db()

  with open('ai2thor_objects.json', 'r', encoding='utf-8') as f:
    objects = json.load(f)

  add_conceptnet(objects)
  add_objects(objects)
  build_walmart_graph(objects)
  add_scene_relations(objects)
  add_receptacle_relations(objects)
  add_material_relations(objects)
  add_ai2thor_action_relations(objects)
  add_parent_relations(objects)
  add_affordances()

  CONN.close()