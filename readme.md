# **user-model**
#### analysing and predicting user paths through a location-based narrative system.
___

### **Getting things up and running**
required python modules:

- **[matplotlib](https://pypi.python.org/pypi/matplotlib)**
    - for GUI components.
    - **instructions**: `pip3 install matplotlib`
- **[osrm-py](https://pypi.python.org/pypi/osrm-py/)**
    - for utilising OSRM for map routing.
    - **instructions**: `pip3 install osrm-py`
- **[SRTM.py](https://pypi.python.org/pypi/SRTM.py)**
    - for utilising SRTM for altitude data.
    - **instructions**: `pip3 install SRTM.py`
- **[numpy](https://pypi.python.org/pypi/numpy)**
    - for use in the machine learning components.
    - **instructions**: `pip3 install numpy`

also needed:

- **[tensorflow](https://www.tensorflow.org)**
    - A machine learning library, for use in the machine learning components.
    - **instructions**:
        - the main guide for installing tensorflow can be found [here](https://www.tensorflow.org/install/).
        - a tensorflow instance must be running when running any code from the `ml` module.
- **[OSRM](http://project-osrm.org)**
    - A routing engine, used by the `walk_dist` ranker and any others that use every heuristic (this includes all the machine learning rankers).
    - **instructions**:
        - main installation instructions depend on platform, and can be found [here](https://github.com/Project-OSRM/osrm-backend/wiki).
        - once installed, instructions for running the backend can be found [here](https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM). However, they are in essence as follows:
            - download a .osm.pbf file corresponding to the area you need from [geofabrik](http://download.geofabrik.de).
            - in the folder you have placed your .osm.pbf file, run
            ```
            osrm-extract your-file.osm.pbf -p path/to/osrm-backend/profiles/car.lua
            osrm-contract your-file.osrm
            ```
            - you will now have a .osrm file, ready to use.
        - to run OSRM, once set up:
            - in the folder with your .osrm file:
            ```
            osrm-routed your-file.osrm
            ```
            - this will start a HTTP server from which the API can be accessed.
            - by default, the server is at `localhost:5000` and this is what the user-model code expects.

### **Basic Usage**

##### *Example usage can be found in the `example.py` file above*

#### **Loading a story**
To load a story from its JSON representation:
```python
myStory = importer.story_from_JSON('My Story File')
```
The function returns a `Story` object for use elsewhere.

#### **Loading user logs**
User logs can also be loaded in from their JSON representation.

To simply load every path in the JSON file for a particular story:
```python
paths_per_reading = importer.path_pages_from_JSON('My Log File', myStory)
```
To try and filter out demo-mode readings from the logs:
```python
paths_per_reading = importer.filtered_paths_from_JSON('My Log File', myStory)
```
This will look for developer user IDs, see if the sequence of paths taken is possible within the constraints of the story and see how fast the user would have been going to determine if a reading may have been in demo-mode. These readings are filtered out.

There is also the `legacy` option to both of these functions (a boolean). If your logs use the old format (ie. if they talk about 'cards'), this must be set to `True`. For newer logs, it can be left as `False` (the default).

These functions will return a dictionary of the format:
```python
paths_per_reading = {
    'reading1-id': [ Page1, Page2, Page3, ..., PageN ]
    ...
    'reading1-id': [ Page1, Page2, Page3, ..., PageN ]
}
```

Where each page is a `Page` object (not just an ID).

To merge two of these dictionaries:
```python
paths_per_reading = importer.merge_paths_per_readings(ppr1, ppr2)
```
This can be useful for having both old and new logs loaded at the same time.

#### **Making a cache**
It is recommended (but not required) to make a cache, which stores the heuristics calculated for each page. This prevents the need to recalculate heuristics when doing many readings. To make a cache:
```python
myCache = cache.Cache()
```

#### **Simulating a reading**
To simulate a reading of the story:
```python
sim_store = traverser.traverse(myStory, rankerFun, deciderFun, cache=myCache)
```
**`rankerFun`** is a function that will take a bunch of pages and produce a score of how 'appealing' each page is. There are several ranker functions in the `ranker` module, for instance `rand` (random), `walk_dist` (walking distance) or `logreg` (logistic regression). Note: before using any machine learning-based rankers (`linreg`, `logreg` or `nn`), their models must be initialised. This is discussed elsewhere.

**`deciderFun`** is a function that takes the output of rankerFun and uses it to choose the next page. There are two decider functions provided in the `decider` module: `rand` (which uses a random number to choose, where pages with a higher score are more likely to be chosen) and `best`, which simply chooses the page with the highest score.

The cache is optional, but recommended.

There are a few other, optional parameters. You can choose the maximum number of steps before the simulation gives up with `max_steps` (default 50). You can specify your own `User` or `Reading` with `user` and `reading`. You can print the progress of the simulation with `prnt`.

The function returns a list of `Record`s. These contain a page (where the user was at this point) and a dictionary of 'options' (the scores of the pages they could go to next).

#### **Simulating many readings**
To simulate *n* readings:
```python
stores = traverser.traverse(myStory, n=50, cache=myCache)
```
This will perform 50 readings, for example.

You can also choose your own ranker and decider here, but they both default to `rand`. This is to assist in trying to find 'unreachable' pages.

#### **Generating a reading from logs**
To generate a reading from user logs:
```python
log_store = traverser.traverse_log(myStory, paths_per_reading)
```
This function will do a simulated reading. However, at each point, the program will go where most people went next from the current page (out of all visible pages). The generated reading can therefore be used as a 'representative' reading of how the users acted in the logs.

The `allow_quitting` option may be set to `True` to enable the traversal to quit the story early, if this was the most popular action. It defaults to `False`.

The returned store's `Record`s have an extra 'page' in their `options`: `0`. This represents the amount of people that quit the story from this page.

#### **Displaying analysis in a GUI window**
To show a GUI with info on the story, logged readings and simulations:
```python
gui.show_all(myStory, paths_per_reading, stores, sim_store, log_store, rankerFun, cache)
```
All of these arguments except the story are optional. If some arguments are left out, some GUI elements will not be shown.

To show a GUI displaying the three key metrics:
```python
gui.show_main_three(myStory, paths_per_reading, stores, sim_store, log_store, rankerFun, cache)
```
#### **Exporting data to a file**
There are many functions to export different forms of information to a `.csv` format:

- `exporter.paths_per_reading_to_csv(paths_per_reading, 'my export file')` for a `paths_per_reading` dictionary.
- `exporter.paths_to_csv(stores, 'my export file')` for a bunch of stores as output by `traverse` or `traverse_log`.
- `exporter.stores_to_CSV(stores, myStory, 'my export file')` to also retain info on `options` from each page.
- `exporter.cache_to_CSV(myCache, 'my export file')` for a `cache`; this can be re-imported later, to further avoid having to calculate heuristics.
- `exporter.regression_to_CSV(myRegressionParams, 'my export file')` for regression parameters (linear or logistic), as output by their respective machine learning functions.
- `exporter.nn_to_CSV(myNN, 'my export file')` for a neural network as output by `ml.nn`.

There are also some functions that output to JSON, where this format makes more sense than csv:

- `cache_to_JSON(myCache, 'my export file')` for a cache. This format can also be re-imported later.
- `stores_to_JSON(stores, 'my export file')` for a list of stores as output by `traverse` or `traverse_log`.

### **More specific info on the modules**
Consult the [wiki](https://github.com/charlie-wt/user-model/wiki).
