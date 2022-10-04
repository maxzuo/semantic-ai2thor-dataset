import setuptools

setuptools.setup(
    name="semantic2thor",
    version="0.0.1",
    author="Max Zuo",
    author_email="max.zuo@gmail.com",
    description="Package to work with and load AI2Thor + semantics dataset",
    long_description="Objects described here are AI2Thor Pickupable objects,\
      combined with information from Conceptnet, Wordnet, RoboCSE, and \
      Walmart embeddings.",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
    ],
    # include_package_data=True,
    package_data={'semantic2thor': [
      'semantic2thor/data/ai2thor.db', 'data/ai2thor.db']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL3 License"
    ]
)
