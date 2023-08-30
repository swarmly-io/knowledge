# knowledge

The knowledge service holds all aspects of what an agent needs to navigate some environment. This includes facts in the form of indexes, functions which combine indexes to form graphs and algorithms to traverse the graph based on constraints and priorities.

It also holds some simple functions to extract data to build indexes.

# Data storage
Indexes are held in elastic search, which offers a simple api to persist facts but search them in the nice Kibana GUI. 

### Finding a path
The key concept of the path finding in knowledge is NEEDS and PROVIDES. The examples are all set in the minecraft world, so an example here would be a player NEEDS a stick AND three diamonds to CRAFT PROVIDE a diamond pickaxe.

This concept allows paths to be formed which can be turned into tasks for downstream services.

### Next best action
In order to determine the next best action for an agent we need to have knowledge of it's goals, present state in the world as well as it's interpretation of it's state.

With these we can correlate it's interpretation with it's goals, selectively adjust the graph to take into account the constraints of it's interpretation, eg. perception of a lack of resource or friendliness of an entity, and real state, for example observations of different entities.

This allows for the selection of the most pressing goals to address, providing a context aware path of what could be done.

### Starting in this service
* Read the tests, see test_app.py for a set of end to end examples.
* Read about networkx, a network declaration and analysis library for python.
* run elastic search 7.13.4 in docker
* run ```pytest```
* start the app using ```python app.py```, check out the postman collection with some pathing examples

