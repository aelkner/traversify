import json
import inspect
import re
from copy import copy, deepcopy


IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z_]\w*$')


def is_identifier(key):
    return IDENTIFIER_REGEX.match(key) is not None


def wrap_value(value, deepcopy=False, filter=None):
    return Traverser(value, deepcopy=deepcopy, filter=filter) if isinstance(value, (list, dict)) else value


def unwrap_value(value):
    return value() if isinstance(value, Traverser) else value


def recursively_unwrap_value(recursive_value):
    recursive_value = unwrap_value(recursive_value)
    if type(recursive_value) == list:
        return [recursively_unwrap_value(v) for v in recursive_value]
    elif type(recursive_value) == dict:
        return dict([(k, recursively_unwrap_value(v)) for k, v in recursive_value.items()])
    return recursive_value


def ensure_list(value):
    return value if type(value) == list else [value]


def split_escaped(path):
    return [k.replace('KQypbNUMED', '.') for
            k in path.replace('..', 'KQypbNUMED').split('.')]


def traverse_path_part(value, part, parts, index, default=None):
    if isinstance(value, list) and not part.isdigit():
        successful_parts = parts[:index + 1]
        msg = "Unable to traverse list via key, '{}', after traversing {}".format(part, successful_parts)
        raise ValueError(msg)
    if part.isdigit():
        return value[int(part)]
    else:
        return value.get(part, default)


def buildout_path(parts, new_value):
    new_path = new_value
    for part in reversed(parts):
        if part.isdigit():
            new_path = [new_path]
        else:
            new_path = {part: new_path}
    return new_path


class Traverser(object):
    def __init__(self, value, deepcopy=True, filter=None):
        if hasattr(value, 'json') and inspect.ismethod(value.json):
            value = value.json()
        if type(value) == type(""):
            value = json.loads(value)
        if not isinstance(value, (list, dict)):
            raise ValueError("Only list or dict types allowed: '{}'".format(value))
        if deepcopy:
            value = recursively_unwrap_value(value)
        self.__traverser__internals__ = {
            'value': value,
            'filter': filter,
        }

    def __call__(self):
        return self.__traverser__internals__['value']

    def to_json(self):
        return json.dumps(self())

    def __dir__(self):
        dir_list = dir(Traverser)
        value = self()
        if type(value) == dict:
            dir_list.extend([k for k in value.keys() if is_identifier(k)])
        return dir_list

    def __getattr__(self, attr, default=None):
        if '__traverser__internals__' in attr:
            return super(Traverser, self).__getattribute__('__traverser__internals__')
        return self.get(attr, default)

    def __setattr__(self, attr, value):
        if '__traverser__internals__' in attr:
            super(Traverser, self).__setattr__('__traverser__internals__', value)
        else:
            self[attr] = value

    def __repr__(self):
        return 'Traverser({})'.format(json.dumps(self(), indent=2, default=str))

    def __str__(self):
        return 'Traverser({})'.format(json.dumps(self(), indent=2, default=str))

    def get(self, attr, default=None):
        parts = split_escaped(attr)
        value = traverse_path_part(self(), parts[0], parts, 0, default=default)
        for index, part in enumerate(parts[1:]):
            if not isinstance(value, (list, dict)):
                return None
            value = traverse_path_part(value, part, parts, index, default=default)
            if value is None:
                return None
        return wrap_value(value)

    def set(self, attr, new_value):
        parts = split_escaped(attr)
        current_value = self()
        for index, part in enumerate(parts[:-1]):
            try:
                value = traverse_path_part(current_value, part, parts, index)
                if value is None:
                    break
            except Exception:
                break
            current_value = value
        else:
            wrapped_value = wrap_value(current_value)
            wrapped_value[parts[-1]] = new_value
            return
        wrapped_value = wrap_value(current_value)
        wrapped_value[part] = buildout_path(parts[index+1:], new_value)

    def ensure_list(self, item):
        value = self.get(item)
        if value is None:
            return None
        if type(value) == type(self):
            return value
        return [value]

    def __getitem__(self, index):
        if type(index) == type(''):
            value = self().get(index)
        else:
            value = self()
            if type(value) != list:
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
        if self.__traverser__internals__['filter'] is None:
            return self() == unwrap_value(other)
        else:
            return self.__traverser__internals__['filter'].are_equal(self, other)

    def prune(self, filter=None):
        if filter is None:
            filter = self.__traverser__internals__['filter']
        if filter is not None:
            filter.prune(self)
        return self

    def __contains__(self, item):
        for value in self:
            if value == item:
                return True
        return False

    def __len__(self):
        value = self()
        return len(value) if type(value) == list else 1

    def __bool__(self):
        return bool(len(self))

    def __delitem__(self, item):
        del self()[item]

    def append(self, item):
        value = self()
        item = unwrap_value(item)
        if type(value) == list:
            value.append(item)
        else:
            self.__traverser__internals__['value'] = [value, item]
        return self

    def extend(self, item):
        value = self()
        items = ensure_list(unwrap_value(item))
        if type(value) == list:
            value.extend(items)
        else:
            self.__traverser__internals__['value'] = [value] + items
        return self

    def __delattr__(self, item):
        del self()[item]

    def __iter__(self):
        value = self()
        if type(value) == list:
            result = []
            for value in value:
                result.append(wrap_value(value))
            return iter(result)
        else:
            return iter([self])

    def __add__(self, item):
        value = ensure_list(self())
        item = ensure_list(unwrap_value(item))
        return wrap_value(value + item)

    def __copy__(self):
        return Traverser(copy(self()))

    def __deepcopy__(self, memo):
        return Traverser(deepcopy(self()))


class Filter(object):
    def __init__(self, blacklist=None, whitelist=None):
        self.blacklist = [] if blacklist is None else ensure_list(blacklist)
        self.whitelist = [] if whitelist is None else ensure_list(whitelist)

    def are_equal(self, left, right):
        left_value = unwrap_value(left)
        right_value = unwrap_value(right)

        if type(left_value) == type(right_value) == list:
            if len(left_value) != len(right_value):
                return False
            for index, item in enumerate(left_value):
                if not self.are_equal(item, right_value[index]):
                    return False
            return True

        elif type(left_value) == type(right_value) == dict:
            left_keys = sorted(left_value.keys())
            right_keys = sorted(right_value.keys())
            if self.blacklist:
                left_keys = [k for k in left_keys if k not in self.blacklist]
                right_keys = [k for k in right_keys if k not in self.blacklist]
            if self.whitelist:
                left_keys = [k for k in left_keys if k in self.whitelist]
                right_keys = [k for k in right_keys if k in self.whitelist]
            if left_keys != right_keys:
                return False
            for key in left_keys:
                if not self.are_equal(left_value[key], right_value[key]):
                    return False
            return True

        else:
            return left_value == right_value

    def prune(self, value):
        value = unwrap_value(value)

        if type(value) == list:
            for item in value:
                self.prune(item)

        elif type(value) == dict:
            keys = list(value.keys())
            if self.blacklist:
                keys = [k for k in keys if k not in self.blacklist]
            if self.whitelist:
                keys = [k for k in keys if k in self.whitelist]
            for key in list(value.keys()):
                if key in keys:
                    self.prune(value[key])
                else:
                    del value[key]
