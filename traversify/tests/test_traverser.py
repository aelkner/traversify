import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from traversify import Traverser, Filter


class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class ConstructorTests(unittest.TestCase):

    def test_invalid(self):
        with self.assertRaises(ValueError):
            Traverser(0)
        with self.assertRaises(ValueError):
            Traverser(0.0)
        with self.assertRaises(ValueError):
            Traverser("abc")

    def test_list(self):
        obj = Traverser([])
        self.assertEqual(obj(), [])

    def test_dict(self):
        obj = Traverser({})
        self.assertEqual(obj(), {})

    def test_json(self):
        obj = Traverser("[]")
        self.assertEqual(obj(), [])
        obj = Traverser("{}")
        self.assertEqual(obj(), {})

    def test_response_object_with_json_method(self):
        obj = Traverser(MockResponse('[]'))
        self.assertEqual(obj, [])

    def test_deepcopy_causes_no_side_effects(self):
        value = {'id': 0}
        obj = Traverser(value)
        obj.id = 1
        self.assertEqual(obj(), {'id': 1})
        self.assertEqual(value, {'id': 0})

    def test_no_deepcopy_causes_intended_side_effects(self):
        value = {'id': 0}
        obj = Traverser(value, deepcopy=False)
        obj.id = 1
        self.assertEqual(obj(), {'id': 1})
        self.assertEqual(value, {'id': 1})

class ConversionToJSONTests(unittest.TestCase):

    def test_to_json(self):
        obj = Traverser({})
        self.assertEqual(obj.to_json(), '{}')
        obj = Traverser([])
        self.assertEqual(obj.to_json(), '[]')


class TraversalTests(unittest.TestCase):

    def test_singleton(self):
        users = {'username': 'jdoe', 'display_name': 'John Doe'}
        obj = Traverser(users)
        self.assertIsNone(obj.invalid_key)
        self.assertEqual(obj.username, 'jdoe')
        self.assertEqual(obj[0].username, 'jdoe')
        self.assertEqual(obj['display_name'], 'John Doe')
        self.assertEqual(obj[0]['display_name'], 'John Doe')

    def test_ensure_list(self):
        obj = Traverser({'item': 'value'})
        self.assertIsNone(obj.ensure_list('invalid_key'))
        self.assertEqual(obj.ensure_list('item'), ['value'])
        obj = Traverser({'item': ['value']})
        self.assertEqual(obj.ensure_list('item')(), ['value'])

    def test_traversal_to_traverser_node(self):
        obj = Traverser({'item': {'key': 'value'}})
        self.assertEqual(obj.item, {'key': 'value'})
        self.assertEqual(obj.item.__class__.__name__, 'Traverser')


class BehaviorTests(unittest.TestCase):

    def test_eq(self):
        obj1 = Traverser({'item': 'value'})
        obj2 = Traverser({'item': 'value'})
        self.assertEqual(obj1, obj2)
        obj2.item = 'foo'
        self.assertNotEqual(obj1, obj2)

    def test_iter(self):
        list_obj = Traverser([123, [456, 789]])
        self.assertEqual(list(list_obj), [123, Traverser([456, 789])])
        singleton = Traverser({'item': 'value'})
        self.assertEqual(list(singleton), [singleton])

    def test_contains(self):
        list_obj = Traverser([123, [456, 789]])
        self.assertTrue(123 in list_obj)
        self.assertTrue([456, 789] in list_obj)
        self.assertTrue(Traverser([456, 789]) in list_obj)
        self.assertFalse(456 in list_obj)

    def test_len(self):
        self.assertEqual(len(Traverser([123, [456, 789]])), 2)
        self.assertEqual(len(Traverser([])), 0)
        self.assertEqual(len(Traverser({})), 1)

    def test_bool(self):
        self.assertTrue(Traverser([123]))
        self.assertFalse(Traverser([]))
        self.assertTrue(Traverser({}))

    def test_add(self):
        obj = Traverser([{'username': 'jdoe'}])
        sum = obj + {'username': 'any'}
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])
        sum = obj + Traverser({'username': 'any'})
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])

    def test_add_to_singleton(self):
        obj = Traverser({'username': 'jdoe'})
        sum = obj + {'username': 'any'}
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])
        sum = obj + Traverser({'username': 'any'})
        self.assertEqual(sum(), [{'username': 'jdoe'}, {'username': 'any'}])


class UpdativeTests(unittest.TestCase):

    def test_setitem(self):
        users = {'username': 'jdoe', 'display_name': 'John Doe'}
        obj = Traverser(users)
        obj.set_to_none = None
        self.assertIsNone(obj.set_to_none)
        obj.id = 123
        self.assertEqual(obj.id, 123)
        obj.roles = ['admin', 'any_user']
        self.assertEqual(obj.roles(), ['admin', 'any_user'])

    def test_setitem_updates_attributes_dict_correctly(self):
        obj = Traverser({})
        obj.new_attr = 'orig_value'
        self.assertEqual(obj.new_attr, 'orig_value')
        obj.new_attr = 'new_value'
        self.assertEqual(obj.new_attr, 'new_value')

    def test_setitem_needing_recursive_unwrap(self):
        obj = Traverser({})
        obj.list_has_traverser = [Traverser([123]), 456]
        self.assertEqual(obj.list_has_traverser(), [[123], 456])
        obj.dict_has_traverser = {'has_traverser': Traverser([123]), 'no_traverser': 456}
        self.assertEqual(sorted(obj.dict_has_traverser().items()), [('has_traverser', [123]), ('no_traverser', 456)])

    def test_setitem_has_no_side_effects(self):
        value = {'username': 'jdoe'}
        obj = Traverser(value)
        obj.id = 1
        self.assertEqual(obj(), {'username': 'jdoe', 'id': 1})
        self.assertEqual(value, {'username': 'jdoe'})

    def test_append(self):
        obj = Traverser([{'username': 'jdoe'}])
        obj.append({'username': 'any'})
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser([{'username': 'jdoe'}])
        obj.append(Traverser({'username': 'any'}))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

    def test_append_to_singleton(self):
        obj = Traverser({'username': 'jdoe'})
        obj.append({'username': 'any'})
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser({'username': 'jdoe'})
        obj.append(Traverser({'username': 'any'}))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

    def test_extend(self):
        obj = Traverser([{'username': 'jdoe'}])
        obj.extend([{'username': 'any'}])
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser([{'username': 'jdoe'}])
        obj.extend(Traverser([{'username': 'any'}]))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])

    def test_extend_singleton(self):
        obj = Traverser({'username': 'jdoe'})
        obj.extend([{'username': 'any'}])
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])
        obj = Traverser({'username': 'jdoe'})
        obj.extend(Traverser([{'username': 'any'}]))
        self.assertEqual(obj(), [{'username': 'jdoe'}, {'username': 'any'}])


class FilterTests(unittest.TestCase):

    def test_blacklist(self):
        id_filter = Filter(blacklist='id')
        left = {'id': 1, 'username': 'jdoe'}
        right = {'username': 'jdoe'}
        self.assertTrue(id_filter.are_equal(left, right))
        self.assertTrue(id_filter.are_equal(left, Traverser(right)))
        self.assertTrue(id_filter.are_equal(Traverser(left), right))
        self.assertTrue(id_filter.are_equal(Traverser(left), Traverser(right)))

    def test_whitelist(self):
        username_filter = Filter(whitelist='username')
        left = {'id': 1, 'username': 'jdoe'}
        right = {'username': 'jdoe'}
        self.assertTrue(username_filter.are_equal(left, right))
        self.assertTrue(username_filter.are_equal(left, Traverser(right)))
        self.assertTrue(username_filter.are_equal(Traverser(left), right))
        self.assertTrue(username_filter.are_equal(Traverser(left), Traverser(right)))

    def test_eq_with_filter(self):
        id_filter = Filter(blacklist='id')
        left = Traverser({'id': 1, 'username': 'jdoe'}, filter=id_filter)
        right = Traverser({'username': 'jdoe'})
        self.assertTrue(left == right)
        self.assertFalse(right == left)

    def test_contains_with_filter(self):
        id_filter = Filter(blacklist='id')
        records = Traverser({'id': 1, 'username': 'jdoe'}, filter=id_filter)
        already_exists_record = Traverser({'username': 'jdoe'})
        self.assertTrue(already_exists_record in records)
        self.assertTrue({'username': 'jdoe'} in records)
        new_record = Traverser({'username': 'foo'})
        self.assertFalse(new_record in records)
        self.assertFalse({'username': 'foo'} in records)

    def test_prune_with_blacklist_filter(self):
        id_filter = Filter(blacklist='id')
        obj = {'id': 1, 'username': 'jdoe'}
        id_filter.prune(obj)
        self.assertTrue(obj == {'username': 'jdoe'})

    def test_prune_with_whitelist_filter(self):
        id_filter = Filter(whitelist='id')
        obj = {'id': 1, 'username': 'jdoe'}
        id_filter.prune(obj)
        self.assertTrue(obj == {'id': 1})

    def test_traverser_prune_no_filter(self):
        obj = Traverser({'id': 1, 'username': 'jdoe'})
        obj.prune()
        self.assertTrue(obj() == {'id': 1, 'username': 'jdoe'})

    def test_traverser_prune_with_blacklist_filter(self):
        id_filter = Filter(blacklist='id')
        obj = Traverser({'id': 1, 'username': 'jdoe'}, filter=id_filter)
        obj.prune()
        self.assertTrue(obj() == {'username': 'jdoe'})

    def test_traverser_prune_with_whitelist_filter(self):
        id_filter = Filter(whitelist='id')
        obj = Traverser({'id': 1, 'username': 'jdoe'}, filter=id_filter)
        obj.prune()
        self.assertTrue(obj() == {'id': 1})

    def test_traverser_prune_called_with_filter(self):
        id_filter = Filter(blacklist='id')
        obj = Traverser({'id': 1, 'username': 'jdoe'})
        obj.prune()
        self.assertTrue(obj() == {'id': 1, 'username': 'jdoe'})
        obj.prune(filter=id_filter)
        self.assertTrue(obj() == {'username': 'jdoe'})


class IDESupportTests(unittest.TestCase):

    def test_dir_for_list(self):
        obj = Traverser([])
        dir_list = sorted([k for k in dir(obj) if not k.startswith('_')])
        self.assertEqual(dir_list, ['append', 'ensure_list', 'extend', 'get', 'prune', 'to_json'])

    def test_dir_for_dict(self):
        obj = Traverser({'id': 1})
        dir_list = sorted([k for k in dir(obj) if not k.startswith('_')])
        self.assertEqual(dir_list, ['append', 'ensure_list', 'extend', 'get', 'id', 'prune', 'to_json'])

    def test_dir_not_including_bad_keys(self):
        obj = Traverser({'id': 1, '@bad': '', 'even.worse': 3})
        dir_list = sorted([k for k in dir(obj) if not k.startswith('_')])
        self.assertEqual(dir_list, ['append', 'ensure_list', 'extend', 'get', 'id', 'prune', 'to_json'])


class CallChainingTests(unittest.TestCase):

    def test_prune_call_chain(self):
        obj = Traverser({})
        self.assertTrue(obj.prune() is obj)

    def test_append_call_chain(self):
        obj = Traverser([])
        self.assertTrue(obj.append({}) is obj)

    def test_extend_call_chain(self):
        obj = Traverser([])
        self.assertTrue(obj.extend([]) is obj)


if __name__ == '__main__':
    unittest.main()
