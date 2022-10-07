from typing import Any, Dict, List, Optional, Tuple

from . import globals
from .metadata import get_object_names
import numpy as np


_conceptnet_dict = None


def conceptnet_dict(cache: bool = True) -> Dict[str, np.ndarray]:
  """
  Load all English Conceptnet numberbatch embeddings.

  The returned dictionary will be quite large, with >500,000 entries. Running
  the `conceptnet` function below is preferred.

  Args:
    cache: Whether or not to cache the results. Makes future calls faster.

  Returns:
    A dict mapping strings and their conceptnet embeddings (if it exists).
  """
  global _conceptnet_dict
  if type(_conceptnet_dict) == dict:
    return _conceptnet_dict

  cur = globals.CONN.execute('SELECT name, embedding FROM conceptnet')
  if cache:
    _conceptnet_dict = {
      name: np.frombuffer(embedding, dtype=np.float32)
      for name, embedding in globals.tqdm(cur.fetchall())}
    return _conceptnet_dict

  return {name: np.frombuffer(embedding, dtype=np.float32)
          for name, embedding in globals.tqdm.globals.tqdm(cur.fetchall())}


def conceptnet(name: str) -> np.ndarray:
  """
  Load English Conceptnet numberbatch embedding for a particular word.

  Args:
    name: Query word to Conceptnet embeddings.

  Returns:
    A single conceptnet embedding of shape (300,) with data type np.float32
    (if it exists).
  """
  if type(_conceptnet_dict) == dict:
    return _conceptnet_dict[name.lower().strip()]

  embedding = globals.CONN.execute('SELECT embedding FROM conceptnet WHERE name LIKE ?',
                           (name.strip(),)).fetchone()
  return np.frombuffer(embedding[0], dtype=np.float32)


def actionable_properties(object_type: str) -> List[str]:
  """
  Retrieve all actionable properties related to a AI2Thor pickupable object.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A list of strings describing the actionable properties of an object, as
    defined by AI2Thor.
  """
  ai2thor_actions = globals.CONN.execute('SELECT ai2thor_action_type, partial FROM ai2thor_actions WHERE object_type LIKE ?', (object_type.strip(),)).fetchall()

  return [action + ' (Some)' * partial for action, partial in ai2thor_actions]


def material_properties(object_type: str) -> List[str]:
  """
  Retrieve all material properties related to a AI2Thor pickupable object.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A list of strings describing the material properties of an object, as
    defined by AI2Thor.
  """
  materials = globals.CONN.execute('SELECT material_property_type FROM material_properties WHERE object_type LIKE ?', (object_type.strip(),)).fetchall()

  return [m[0] for m in materials]


def scenes(object_type: str) -> List[str]:
  """
  Retrieve all scenes where a AI2Thor pickupable object can be found.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A list of strings describing all scenes where a AI2Thor pickupable object
    can be found, as defined by AI2Thor.
  """
  _scenes = globals.CONN.execute('SELECT scene_type FROM scenes WHERE object_type LIKE ?', (object_type.strip(),)).fetchall()

  return [s[0] for s in _scenes]


def receptacles(object_type: str) -> List[str]:
  """
  Retrieve all default compatible receptacles of a AI2Thor pickupable object.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A list of strings describing all default compatible receptacles where a
    AI2Thor pickupable object can be found, as defined by AI2Thor.
  """
  _receptacles = globals.CONN.execute('SELECT receptacle_type FROM receptacles WHERE object_type LIKE ?', (object_type.strip(),)).fetchall()

  return [s[0] for s in _receptacles]

def affordances(object_type: str) -> Tuple[Dict[str, bool], Optional[np.ndarray]]:
  """
  Retrieve RoboCSE properties and embedding of a AI2Thor pickupable object.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A dict of strings to bool describing the RoboCSE properties of a
    AI2Thor pickupable object, as defined by RoboCSE.

    A np.ndarray of the same properties, decomposed by PCA to 20 dimensions from
    24 total properties.
  """
  cur = globals.CONN.execute('PRAGMA table_info(robocse)')
  cse_types = cur.fetchall()
  cse_types = [a[1] for a in filter(lambda a: a[2] == 'bool', cse_types)]

  cse = globals.CONN.execute(f'SELECT {", ".join(cse_types)}, pca_embedding FROM robocse WHERE object_type LIKE ?', (object_type.strip(),)).fetchone()
  if cse is None:
    return {}, None

  *cse, pca = cse
  return {a_type: bool(a) for a_type, a in zip(cse_types, cse)}, np.frombuffer(pca, dtype=np.float32)


def walmart(object_type: str) -> List[List[str]]:
  """
  Retrieve Walmart path of a AI2Thor pickupable object.

  Args:
    object_type: name of a AI2Thor pickupable object.

  Returns:
    A list of paths (each path a list of strings) that describe an object
    according to the Walmart website's categorization.
  """
  def _walmart(node: str, path: List[str]) -> List[str]:
    curr = globals.CONN.execute('SELECT parent FROM walmart WHERE node LIKE ?', (node.strip(),)).fetchone()[0]
    if not curr:
      return path[::-1]
    path.append(curr)

    return _walmart(curr, path)

  parents = globals.CONN.execute('SELECT parent FROM object_parents WHERE object_type LIKE ?', (object_type.strip(),)).fetchall()

  if not len(parents):
    return parents

  return [_walmart(parent[0], [parent[0]]) for parent in parents]


def load(object_type: str) -> Dict[str, Any]:
  """
  Retrieve all attributes of a AI2Thor pickupable Object

  Args:
    object_type: name of a AI2Thor pickupable object

  Returns:
    A dict of properties:
      Object Type: The AI2Thor object_type, same as argument,
        corrected for small differences (capitalization, spaces, etc.)
      Scenes: A list of strings describing all scenes where a AI2Thor pickupable
        object can be found, as defined by AI2Thor.
      Actionable Properties: A list of strings describing the actionable
        properties of an object, as defined by AI2Thor.
      Material Properties: A list of strings describing the material properties
        of an object, asdefined by AI2Thor.
      paths: A list of paths (each path a list of strings) that describe an
        object according to the Walmart website's categorization.
      Affordances: A dict of strings to bool describing the affordances of a
        AI2Thor pickupableobject, as defined by RoboCSE.
      RoboCSE: A dict of strings to bool describing the RoboCSE properties of a
        AI2Thor pickupable object, as defined by RoboCSE.
      RoboCSE Embedding: A np.ndarray of the same properties, decomposed by PCA
        to 20 dimensions from 24 total properties.
      Conceptnet Name: Corresponding conceptnet name for a AI2Thor object.
      Conceptnet Embedding: Corresponding conceptnet embedding for a AI2Thor
        object.
      Wordnet Name: Corresponding wordnet name for a AI2Thor object.
      Contextual Interactions: Context as defined by AI2Thor.
  """
  _object_type, conceptnet_name, wordnet_name, context = globals.CONN.execute(
    'SELECT name, conceptnet_name, wordnet_name, contextual_interactions FROM objects WHERE name LIKE ?', (object_type.strip(),)).fetchone()

  conceptnet_embedding = conceptnet(conceptnet_name)
  ai2thor_actions = actionable_properties(object_type)
  materials = material_properties(object_type)
  _scenes = scenes(object_type)
  _receptacles = receptacles(object_type)
  _robocse, robocse_embedding = affordances(object_type)
  paths = walmart(object_type)

  return {
            'Object Type': _object_type,
            'Scenes': _scenes,
            'Actionable Properties': ai2thor_actions,
            'Material Properties': materials,
            'Default Compatible Receptacles': _receptacles,
            'paths': paths,
            'Affordances': _robocse,
            'RoboCSE Embedding': robocse_embedding,
            'Conceptnet Name': conceptnet_name,
            'Conceptnet Embedding': conceptnet_embedding,
            'Wordnet Name': wordnet_name,
            'Contextual Interactions': context
          }


def load_all() -> Dict[str, Dict[str, Any]]:
  return {name: load(name) for name in globals.tqdm(get_object_names())}
