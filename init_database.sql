
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS walmart;
CREATE TABLE walmart (
  node text NOT NULL,
  parent text,
  PRIMARY KEY (node),
  FOREIGN KEY (parent) REFERENCES walmart(node)
);

INSERT INTO walmart VALUES ('Object', NULL);

DROP TABLE IF EXISTS conceptnet;
CREATE TABLE conceptnet (
  name text NOT NULL,
  embedding blob NOT NULL,
  PRIMARY KEY (name)
);

DROP TABLE IF EXISTS ai2thor_action_types;
CREATE TABLE ai2thor_action_types (
  name text NOT NULL,
  partial bool NOT NULL,
  PRIMARY KEY (name, partial)
);

INSERT INTO ai2thor_action_types VALUES ('Breakable', False),
                                    ('Breakable', True),
                                    ('Cookable', False),
                                    ('Dirtyable', False),
                                    ('Fillable', False),
                                    ('Openable', False),
                                    ('Pickupable', False),
                                    ('Receptacle', False),
                                    ('Sliceable', False),
                                    ('Toggleable', False),
                                    ('UsedUp', False),
                                    ('UsedUp', True);

DROP TABLE IF EXISTS scene_types;
CREATE TABLE scene_types (
  name text NOT NULL,
  PRIMARY KEY (name)
);

INSERT INTO scene_types VALUES ('Bathrooms'), ('Bedrooms'), ('Kitchens'), ('Living Rooms');

DROP TABLE IF EXISTS material_property_types;
CREATE TABLE material_property_types (
  name text NOT NULL,
  PRIMARY KEY (name)
);

INSERT INTO material_property_types VALUES ('Break'), ('Mass'), ('SalientMaterials'), ('Slice'), ('Temperature');

DROP TABLE IF EXISTS receptacle_types;
CREATE TABLE receptacle_types (
  name text NOT NULL,
  PRIMARY KEY (name)
);

INSERT INTO receptacle_types VALUES ('ArmChair'),
  ('Bathtub'),
  ('BathtubBasin'),
  ('Bed'),
  ('Bowl'),
  ('Box'),
  ('Cabinet'),
  ('Cart'),
  ('CoffeeTable'),
  ('CounterTop'),
  ('Cup'),
  ('Desk'),
  ('DiningTable'),
  ('Drawer'),
  ('Dresser'),
  ('Fridge'),
  ('GarbageCan'),
  ('HandTowelHolder'),
  ('LaundryHamper'),
  ('Microwave'),
  ('Mug'),
  ('Ottoman'),
  ('Pan'),
  ('Plate'),
  ('Pot'),
  ('Safe'),
  ('Shelf'),
  ('SideTable'),
  ('Sink'),
  ('SinkBasin'),
  ('Sofa'),
  ('StoveBurner'),
  ('TVStand'),
  ('Toaster'),
  ('Toilet'),
  ('ToiletPaperHanger'),
  ('TowelHolder');

DROP TABLE IF EXISTS objects;
CREATE TABLE objects (
  name text NOT NULL,
  conceptnet_name text NOT NULL,
  wordnet_name text,
  contextual_interactions text,
  flag int NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (conceptnet_name) REFERENCES conceptnet(name)
);

DROP TABLE IF EXISTS object_parents;
CREATE TABLE object_parents (
  object_type text NOT NULL,
  parent text NOT NULL,
  PRIMARY KEY (object_type, parent),
  FOREIGN KEY (object_type) REFERENCES objects(name),
  FOREIGN KEY (parent) REFERENCES walmart(node)
);

DROP TABLE IF EXISTS ai2thor_actions;
CREATE TABLE ai2thor_actions (
  object_type text NOT NULL,
  ai2thor_action_type text NOT NULL,
  partial bool not NULL,
  PRIMARY KEY (object_type, ai2thor_action_type, partial),
  FOREIGN KEY (object_type) REFERENCES objects(name),
  FOREIGN KEY (ai2thor_action_type, partial) REFERENCES ai2thor_action_types(name, partial)
);

DROP TABLE IF EXISTS affordances;
-- affordances table created dynamically

DROP TABLE IF EXISTS robocse;
-- robocse table created dynamically

DROP TABLE IF EXISTS scenes;
CREATE TABLE scenes (
  object_type text NOT NULL,
  scene_type text NOT NULL,
  PRIMARY KEY (object_type, scene_type),
  FOREIGN KEY (object_type) REFERENCES objects(name),
  FOREIGN KEY (scene_type) REFERENCES scene_types(name)
);

DROP TABLE IF EXISTS material_properties;
CREATE TABLE material_properties (
  object_type text NOT NULL,
  material_property_type text NOT NULL,
  PRIMARY KEY (object_type, material_property_type),
  FOREIGN KEY (object_type) REFERENCES objects(name),
  FOREIGN KEY (material_property_type) REFERENCES material_property_types(name)
);

DROP TABLE IF EXISTS receptacles;
CREATE TABLE receptacles (
  object_type text NOT NULL,
  receptacle_type text NOT NULL,
  PRIMARY KEY (object_type, receptacle_type),
  FOREIGN KEY (object_type) REFERENCES objects(name),
  FOREIGN KEY (receptacle_type) REFERENCES receptacle_types(name)
);