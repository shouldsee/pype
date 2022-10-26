from collections import OrderedDict
def make_SafeOrderedDict(_eletype):
    class _SafeOrderedDict(SafeOrderedDict):
        eletype = _eletype
    return _SafeOrderedDict
class SafeOrderedDict(OrderedDict):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as regular dictionaries.

    # The internal self.__map dict maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel is in self.__hardroot with a weakref proxy in self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted from an OrderedDict.
    eletype = None

    def __setitem__(self, key, value):
        if not isinstance(value, self.eletype):
            raise TypeError(
            f'Setting key {key}, value must be of {self.eletype}'
            f' but found {value.__class__}')
        super().__setitem__( key, value)

    # def __setitem__(self, key, value,
    #                 dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
    #     # 'od.__setitem__(i, y) <==> od[i]=y'
    #     # Setting a new item creates a new link at the end of the linked list,
    #     # and the inherited dictionary is updated with the new key/value pair.
    #     if key not in self:
    #         self.__map[key] = link = Link()
    #         root = self.__root
    #         last = root.prev
    #         link.prev, link.next, link.key = last, root, key
    #         last.next = link
    #         root.prev = proxy(link)
    #     assert isinstance(value, self,eletype)
    #     super().__setitem__(key,value)
    #     dict_setitem(self, key, value)

    # def __delitem__(self, key, dict_delitem=dict.__delitem__):
    #     'od.__delitem__(y) <==> del od[y]'
    #     # Deleting an existing item uses self.__map to find the link which gets
    #     # removed by updating the links in the predecessor and successor nodes.
    #     dict_delitem(self, key)
    #     link = self.__map.pop(key)
    #     link_prev = link.prev
    #     link_next = link.next
    #     link_prev.next = link_next
    #     link_next.prev = link_prev
    #     link.prev = None
    #     link.next = None

    # def __iter__(self):
    #     'od.__iter__() <==> iter(od)'
    #     # Traverse the linked list in order.
    #     root = self.__root
    #     curr = root.next
    #     while curr is not root:
    #         yield curr.key
    #         curr = curr.next

    # def __reversed__(self):
    #     'od.__reversed__() <==> reversed(od)'
    #     # Traverse the linked list in reverse order.
    #     root = self.__root
    #     curr = root.prev
    #     while curr is not root:
    #         yield curr.key
    #         curr = curr.prev

    # def clear(self):
    #     'od.clear() -> None.  Remove all items from od.'
    #     root = self.__root
    #     root.prev = root.next = root
    #     self.__map.clear()
    #     dict.clear(self)

    # def popitem(self, last=True):
    #     '''Remove and return a (key, value) pair from the dictionary.
    #     Pairs are returned in LIFO order if last is true or FIFO order if false.
    #     '''
    #     if not self:
    #         raise KeyError('dictionary is empty')
    #     root = self.__root
    #     if last:
    #         link = root.prev
    #         link_prev = link.prev
    #         link_prev.next = root
    #         root.prev = link_prev
    #     else:
    #         link = root.next
    #         link_next = link.next
    #         root.next = link_next
    #         link_next.prev = root
    #     key = link.key
    #     del self.__map[key]
    #     value = dict.pop(self, key)
    #     return key, value

    # def move_to_end(self, key, last=True):
    #     '''Move an existing element to the end (or beginning if last is false).
    #     Raise KeyError if the element does not exist.
    #     '''
    #     link = self.__map[key]
    #     link_prev = link.prev
    #     link_next = link.next
    #     soft_link = link_next.prev
    #     link_prev.next = link_next
    #     link_next.prev = link_prev
    #     root = self.__root
    #     if last:
    #         last = root.prev
    #         link.prev = last
    #         link.next = root
    #         root.prev = soft_link
    #         last.next = link
    #     else:
    #         first = root.next
    #         link.prev = root
    #         link.next = first
    #         first.prev = soft_link
    #         root.next = link

    # def __sizeof__(self):
    #     sizeof = _sys.getsizeof
    #     n = len(self) + 1                       # number of links including root
    #     size = sizeof(self.__dict__)            # instance dictionary
    #     size += sizeof(self.__map) * 2          # internal dict and inherited dict
    #     size += sizeof(self.__hardroot) * n     # link objects
    #     size += sizeof(self.__root) * n         # proxy objects
    #     return size

    # update = __update = _collections_abc.MutableMapping.update

    # # def update(self, other=(), /, **kwds):
    # #     ''' D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
    # #         If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
    # #         If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
    # #         In either case, this is followed by: for k, v in F.items(): D[k] = v
    # #     '''
    # #     if isinstance(other, Mapping):
    # #         for key in other:
    # #             self[key] = other[key]
    # #     elif hasattr(other, "keys"):
    # #         for key in other.keys():
    # #             self[key] = other[key]
    # #     else:
    # #         for key, value in other:
    # #             self[key] = value
    # #     for key, value in kwds.items():
    # #         self[key] = value

    # def keys(self):
    #     "D.keys() -> a set-like object providing a view on D's keys"
    #     return _OrderedDictKeysView(self)

    # def items(self):
    #     "D.items() -> a set-like object providing a view on D's items"
    #     return _OrderedDictItemsView(self)

    # def values(self):
    #     "D.values() -> an object providing a view on D's values"
    #     return _OrderedDictValuesView(self)

    # __ne__ = _collections_abc.MutableMapping.__ne__

    # __marker = object()

    # def pop(self, key, default=__marker):
    #     '''od.pop(k[,d]) -> v, remove specified key and return the corresponding
    #     value.  If key is not found, d is returned if given, otherwise KeyError
    #     is raised.
    #     '''
    #     marker = self.__marker
    #     result = dict.pop(self, key, marker)
    #     if result is not marker:
    #         # The same as in __delitem__().
    #         link = self.__map.pop(key)
    #         link_prev = link.prev
    #         link_next = link.next
    #         link_prev.next = link_next
    #         link_next.prev = link_prev
    #         link.prev = None
    #         link.next = None
    #         return result
    #     if default is marker:
    #         raise KeyError(key)
    #     return default

    # def setdefault(self, key, default=None):
    #     '''Insert key with a value of default if key is not in the dictionary.
    #     Return the value for key if key is in the dictionary, else default.
    #     '''
        
    #     if key in self:
    #         return self[key]
    #     self[key] = default
    #     return default

    # @_recursive_repr()
    # def __repr__(self):
    #     'od.__repr__() <==> repr(od)'
    #     if not self:
    #         return '%s()' % (self.__class__.__name__,)
    #     return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    # def __reduce__(self):
    #     'Return state information for pickling'
    #     state = self.__getstate__()
    #     if state:
    #         if isinstance(state, tuple):
    #             state, slots = state
    #         else:
    #             slots = {}
    #         state = state.copy()
    #         slots = slots.copy()
    #         for k in vars(OrderedDict()):
    #             state.pop(k, None)
    #             slots.pop(k, None)
    #         if slots:
    #             state = state, slots
    #         else:
    #             state = state or None
    #     return self.__class__, (), state, None, iter(self.items())

    # def copy(self):
    #     'od.copy() -> a shallow copy of od'
    #     return self.__class__(self)

    # @classmethod
    # def fromkeys(cls, iterable, value=None):
    #     '''Create a new ordered dictionary with keys from iterable and values set to value.
    #     '''
    #     self = cls()
    #     for key in iterable:
    #         self[key] = value
    #     return self

    # def __eq__(self, other):
    #     '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
    #     while comparison to a regular mapping is order-insensitive.
    #     '''
    #     if isinstance(other, OrderedDict):
    #         return dict.__eq__(self, other) and all(map(_eq, self, other))
    #     return dict.__eq__(self, other)

    # def __ior__(self, other):
    #     self.update(other)
    #     return self

    # def __or__(self, other):
    #     if not isinstance(other, dict):
    #         return NotImplemented
    #     new = self.__class__(self)
    #     new.update(other)
    #     return new

    # def __ror__(self, other):
    #     if not isinstance(other, dict):
    #         return NotImplemented
    #     new = self.__class__(other)
    #     new.update(self)
    #     return new

