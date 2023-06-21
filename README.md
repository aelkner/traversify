# traversify

Handy python classes for manipulating json data, providing syntactic sugar for less verbose, easier to write code.

Traverser class allows one to:

* traverse complex trees of data with dotted syntax rather than the verbose dictionary dereferencing.
* treat nodes on the tree as lists even if they are singleton dictionaries, eliminating a lot of type-checking code.
* add or delete branches of the tree with simple dotted syntax.
* treat missing keys on the tree as None rather than throwing a key exception, much as JavaScript returns undefined.
* linkage to Filter class (defined next) for powerful tree comparisons or tree pruning.

Filter class allows one to:

* define a set of criteria for comparing two partially incongruous trees by limiting the sets of fields compared.
* apply said criteria to prune a tree of any unwanted fields.

# Traverser

Pass tree data to Traverser, either as a list, dictionary, json string or any class offering a json method, and the resultant object will provide the syntactic sugar for traversing with dotted syntax, treating singleston nodes as lists:

```pycon
>>> from traversify import Traverser
>>> obj = Traverser({'id': 1, 'username': 'jdoe'})
>>> obj.id
1
>>> obj.username
'jdoe'
>>> obj.bad_key is None
True
>>> [node.id for node in obj]
[1]
>>> obj[0].id
1
>>> {'id': 1, 'username': 'jdoe'} in obj
True
```

Not only  can singletons be addressed as lists, but append and extend methods are available to turn singletons into lists on the fly:

```pycon
>>> obj = Traverser({'id': 1})
>>> obj.append({'id': 2})
>>> obj.extend([{'id': 3, 'id': 4}])
>>> [node.id for node in obj]
[1, 2, 3, 4]
```

At any time, a Traverser instance will return the underlying value when called:

```pycon
>>> obj = Traverser({'id': 1})
>>> obj()
{'id': 1}
```

The tree can be updated using dotted syntax.  Note that by default, a Traverser instance makes a deepcopy of the json data so that there are no unintended side effects:

```pycon
>>> data = {'id': 1, 'username': 'jdoe'}
>>> obj = Traverser(data)
>>> obj.id = 2
>>> del obj.username
>>> obj()
{'id': 2}
>>> data
{'id': 1, 'username': 'jdoe'}
```

However, if the side-effect of updating the data passed is desired (perhaps due to memory constaints), then pass deepcopy=False:

```pycon
>>> data = {'id': 1}
>>> obj = Traverser(data, deepcopy=False)
>>> obj.id = 2
>>> obj()
{'id': 2}
>>> data
{'id': 2}
```

In case there are keys that are not identifiers, then dictionary dereferencing can still be used:

```pycon
>>> obj = Traverser({'@xsi.type': 'textarea'})
>>> obj['@xsi.type']
'textarea'
```

The get method allows traversing multiple levels in one call, using dots to set off the levels:
```pycon
>>> obj = Traverser({'root': {'username': 'any'}})
>>> obj.get('root.username')
'any'
```

Also, the get method supports dot-escaping so that keys containing dots can still be traversed:

```pycon
>>> obj = Traverser({'@xsi.type': 'textarea'})
>>> obj.get('@xsi..type')
'textarea'
```

There's a set method that will update a node multiple levels down and even build out branches that aren't already there:

```pycon
>>> obj = Traverser({'stats': {'id': 1}})
>>> obj.set('stats.id', 2)
>>> obj()
{'stats': {'id': 2}}
>>> obj.set('users.0.username', 'any')
>>> obj()
{'stats': {'id': 2}, 'users': [{'username': 'any'}]}
```

To save the trouble of importing json and using dumps, there's a handy to_json method:

```pycon
>>> obj = Traverser({'id': 1})
>>> obj.to_json()
'{"id": 1}'
```

Example:
``data = requests.get("https://datausa.io/api/data?drilldowns=Nation&measures=Population").json()``

extract subtree of sources:

```pycon
>>> Traverser(data).subTree('source.0.annotations')
Traverser({
  "source_name": "Census Bureau",
  "source_description": "The American Community Survey (ACS) is conducted by the US Census and sent to a portion of the population every year.",
  "dataset_name": "ACS 5-year Estimate",
  "dataset_link": "http://www.census.gov/programs-surveys/acs/",
  "table_id": "B01003",
  "topic": "Diversity",
  "subtopic": "Demographics"
})
```

extract list of subtree's :

```pycon
>>> Traverser(data).subTreeArray("data")[0]
Traverser({
  "ID Nation": "01000US",
  "Nation": "United States",
  "ID Year": 2020,
  "Year": "2020",
  "Population": 326569308,
  "Slug Nation": "united-states"
})
```

extract list of subtree's and query using list comprehension :

```pycon
>>> [data for data in Traverser(data).subTreeArray("data") if data.Year == "2020"]
[Traverser({
  "ID Nation": "01000US",
  "Nation": "United States",
  "ID Year": 2020,
  "Year": "2020",
  "Population": 326569308,
  "Slug Nation": "united-states"
})]
```

filter a tree (whitelist)

```pycon
>>> Traverser(data).filter(['source.0.annotations.source_name', 'source.0.annotations.topic', 'source.0.annotations.subtopic'])
Traverser({
  "source_name": "Census Bureau",
  "topic": "Diversity",
  "subtopic": "Demographics"
})
```
extract list of subtree's and query using list comprehension, filter nation and year
```pycon
>>> [data.filter(['Year','Nation']) for data in Traverser(data).subTreeArray("data")]
[Traverser({
  "Year": "2020",
  "Nation": "United States"
}), Traverser({
  "Year": "2019",
  "Nation": "United States"
}), Traverser({
  "Year": "2018",
  "Nation": "United States"
}),
...]
```

extract list of subtree's and query using list comprehension, prune out ID Nation and ID Year
```pycon
>>> [data.prune(['ID Nation','ID Year']) for data in Traverser(data).subTreeArray("data")]
[Traverser({
  "Nation": "United States",
  "Year": "2020",
  "Population": 326569308,
  "Slug Nation": "united-states"
}), Traverser({
  "Nation": "United States",
  "Year": "2019",
  "Population": 324697795,
  "Slug Nation": "united-states"
}), Traverser({
  "Nation": "United States",
  "Year": "2018",
  "Population": 322903030,
  "Slug Nation": "united-states"
})
...]
```

# Filter

Often one needs to compare two trees without taking into account irrelavant fields, like when records in the tree have ids, but a new record doesn't have it yet.  Filter provides a way to make this less verbose by providing blacklist and whitelist attributes for controlled comparison:

```pycon
>>> from traversify import Traverser, Filter
>>> id_exclude_filter = Filter(blacklist='id')
>>> record = Traverser({'id': 1, 'username': 'jdoe'})
>>> id_exclude_filter.are_equal(record, {'username': 'jdoe'})
True
```

The same filter can be used to prune a tree of its unwanted fields:

```pycon
>>> id_exclude_filter.prune(record)
>>> record()
{'username': 'jdoe'}
```

If a filter is passed while creating a Traverser instance, then `==`, `in` and the `prune()` method will use it to do the comparison or pruning:

```pycon
>>> record = Traverser({'id': 1, 'username': 'jdoe'}, filter=Filter(blacklist='id'))
>>> record == {'username': 'jdoe'}
True
>>> {'username': 'jdoe'} in record
True
>>> record.prune()
>>> record()
{'username': 'jdoe'}
```

Traverser's prune method will accept a filter to override the default (or supply one not already supplied):

```pycon
>>> record = Traverser({'id': 1, 'username': 'jdoe'})
>>> record.prune(filter=Filter(blacklist='id'))
>>> record()
{'username': 'jdoe'}
```
