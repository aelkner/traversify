class Traverser(object):
    def __init__(self, value):
        if type(value) not in [type([]), type({})]:
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

    @staticmethod
    def wrap_value(value):
        return Traverser(value) if type(value) in [type({}), type([])] else value

    @staticmethod
    def unwrap_value(value):
        return value() if isinstance(value, Traverser) else value

    def get(self, attr, default=None):
        value = self().get(attr, default)
        return self.wrap_value(value)

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
            return self.wrap_value(value)

    def __setitem__(self, index, value):
        self()[index] = self.unwrap_value(value)

    def __contains__(self, item):
        return item in self()

    def __len__(self):
        return len(self())

    def __bool__(self):
        return bool(self())

    def __delitem__(self, item):
        del self()[item]

    def append(self, other):
        self().append(self.unwrap_value(other))

    def __delattr__(self, item):
        del self()[item]

    def __iter__(self):
        value = self()
        if type(value) in [type({}), type([])]:
            if type(value) != type([]):
                value = [value]
            result = []
            for value in value:
                result.append(Traverser(value) if type(value) in [type({}), type([])] else value)
            return iter(result)
        return iter(self())

    def __add__(self, other):
        return Traverser(self() + self.unwrap_value(other))

    def __copy__(self):
        return Traverser(copy(self()))

    def __deepcopy__(self, memo):
        return Traverser(deepcopy(self()))

