# Semantic2Thor Dataset
This is a pip-installable package that can be installed directly from git
(see below).

The Semantic2Thor dataset incorporates more semantic information to the AI2Thor
dataset, specifically for all objects with the "Pickupable" property.
Corresponding Conceptnet numberbatch embeddings are provided, alongside the
closest corresponding wordnet name. For each object, a "Walmart Embedding" is
also provided, which describes the categorization of an item based on the
[Walmart website](https://www.walmart.com). Finally, information from the
[RoboCSE](https://adaruna3.github.io/robocse/) dataset is used to describe
affordances. We generate an affordance vector embedding for each object off
the RoboCSE properties using PCA.


## Install
From your terminal, with your preferred Python 3 environment enabled, run the
following:

```bash
pip install git+https://github.com/maxzuo/semantic-ai2thor-dataset
```
Or:
```bash
pip3 install git+https://github.com/maxzuo/semantic-ai2thor-dataset
```

## Usage
The Semantic2Thor package provides a wrapper API to the dataset which serves two
main functionalities: retrieving metadata, and loading object data.

For metadata, use the metadata submodule:
```python
import semantic2thor

object_types = semantic2thor.metadata.get_object_names()
```
Or:
```python
from semantic2thor import metadata

affordance_types = metadata.get_affordance_types()
```

For loading objects or actual embeddings, here are some example function calls:
```python
import semantic2thor

conceptnet_embeddings = semantic2thor.conceptnet_dict()
apple_conceptnet = semantic2thor.conceptnet('apple')

obj = semantic2thor.load('tabletopdecor')
all_objs = semantic2thor.load_all()
```

All forward facing functionalities are type-hinted documented with docstrings.


### "Advanced" Usage
Not really advanced, but for things that aren't covered in our API, you can
directly query the database:
```python
import semantic2thor

semantic2thor.globals.CONN.execute(...)
```


## Dependencies
Pip installing this package, either from a clone of this repo or directly from
GitHub, will automatically load any and all dependencies.

The required dependencies are minimal:
* `numpy`


The [`tqdm` package](https://pypi.org/project/tqdm/) is an optional dependency.
If the package is installed, loading times for large loading tasks will be
presented with a progress bar.