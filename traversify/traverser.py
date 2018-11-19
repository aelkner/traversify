import json


def traversable(value):
    return type(value) in [type([]), type({})]


def wrap_value(value):
    return Traverser(value) if type(value) in [type({}), type([])] else value


def unwrap_value(value):
    return value() if isinstance(value, Traverser) else value


def recursively_unwrap_value(recursive_value):
    recursive_value = unwrap_value(recursive_value)
    if type(recursive_value) == type([]):
        return [recursively_unwrap_value(v) for v in recursive_value]
    elif type(recursive_value) == type({}):
        return dict([(k, recursively_unwrap_value(v)) for k, v in recursive_value.items()])
    return recursive_value


class Traverser(object):
    def __init__(self, value):
        if type(value) == type(""):
            value = json.loads(value)
        if not traversable(value):
            raise ValueError("Only list or dict types allowed: '{}'".format(value))
        self.__traversify__value = value

    def __call__(self):
        return self.__traversify__value

    def __getattr__(self, attr, default=None):
        if '__traversify__value' in attr:
            return super(Traverser, self).__getattribute__('__traversify__value')
        return self.get(attr, default)

    def __setattr__(self, attr, value):
        if '__traversify__value' in attr:
            super(Traverser, self).__setattr__('__traversify__value',  value)
        else:
            self[attr] = value

    def __repr__(self):
        return 'Traverser({})'.format(self())

    def get(self, attr, default=None):
        value = self().get(attr, default)
        return wrap_value(value)

    def ensure_list(self, item):
        value = self.get(item)
        if value is None:
            return None
        if type(value) == type(self):
            return value
        return [value]

    def __getitem__(self, index):
        if type(index) == type(''):
            return self.get(index)
        else:
            value = self()
            if type(value) != type([]):
                value = [value]
            if type(index) == type(slice(0)):
                start = 0 if index.start is None else index.start
                stop = len(value) if index.stop is None else index.stop
                value = value[start:stop]
            else:
                value = value[index]
            return wrap_value(value)

    def __setitem__(self, index, value):
        self()[index] = recursively_unwrap_value(value)

    def __eq__(self, other):
        return self() == other()

    def __contains__(self, item):
        value = self()
        item = unwrap_value(item)
        return item in value

    def __len__(self):
        value = self()
        return len(value) if type(value) == type([]) else 1

    def __bool__(self):
        return bool(len(self))

    def __delitem__(self, item):
        del self()[item]

    def append(self, other):
        self().append(unwrap_value(other))

    def __delattr__(self, item):
        del self()[item]

    def __iter__(self):
        value = self()
        if type(value) == type([]):
            result = []
            for value in value:
                result.append(Traverser(value) if traversable(value) else value)
            return iter(result)
        else:
            return iter([self])

    def __add__(self, other):
        return Traverser(self() + unwrap_value(other))

    def __copy__(self):
        return Traverser(copy(self()))

    def __deepcopy__(self, memo):
        return Traverser(deepcopy(self()))
