from typing import List

from .globals import *
import numpy as np


def get_affordance_types() -> List[str]:
  """
  Get all unique RoboCSE affordance types.

  Returns:
    A list of strings describing all RoboCSE affordances.
  """
  cur = CONN.execute('PRAGMA table_info(affordances)')
  affordances = cur.fetchall()

  return [item[1] for item in filter(lambda a: a[2] == 'bool', affordances)]


def get_robocse_types() -> List[str]:
  """
  Get all unique RoboCSE types.

  Returns:
    A list of strings describing all RoboCSE properties.
  """
  cur = CONN.execute('PRAGMA table_info(robocse)')
  affordances = cur.fetchall()

  return [item[1] for item in filter(lambda a: a[2] == 'bool', affordances)]


def get_ai2thor_actionable_types() -> List[str]:
  """
  Get all unique AI2Thor actionable properties as defined by AI2Thor.

  Returns:
    A list of strings describing all AI2Thor actionable properties.
  """
  cur = CONN.execute('SELECT DISTINCT name FROM ai2thor_action_types')
  ai2thor_actionables = cur.fetchall()

  return [item[0] for item in ai2thor_actionables]


def get_material_property_types() -> List[str]:
  """
  Get all unique AI2Thor material properties as defined by AI2Thor.

  Returns:
    A list of strings describing all AI2Thor material properties.
  """
  cur = CONN.execute('SELECT DISTINCT name FROM material_property_types')
  material_property_types = cur.fetchall()

  return [item[0] for item in material_property_types]


def get_receptacle_types() -> List[str]:
  """
  Get all unique AI2Thor receptacles as defined by AI2Thor.

  Returns:
    A list of strings describing all AI2Thor receptacles.
  """
  cur = CONN.execute('SELECT DISTINCT name FROM receptacle_types')
  receptacle_types = cur.fetchall()

  return [item[0] for item in receptacle_types]


def get_scene_types() -> List[str]:
  """
  Get all unique AI2Thor scenes as defined by AI2Thor.

  Returns:
    A list of strings describing all AI2Thor scenes.
  """
  cur = CONN.execute('SELECT DISTINCT name FROM scene_types')
  scene_types = cur.fetchall()

  return [item[0] for item in scene_types]


def get_object_names() -> List[str]:
  """
  Get all unique AI2Thor objects with Pickupable action attribute.

  Returns:
    A list of strings describing all AI2Thor objects with Pickupable action
    attribute.
  """
  cur = CONN.execute('SELECT DISTINCT name FROM objects')
  object_types = cur.fetchall()

  return [item[0] for item in object_types]
