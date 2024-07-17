import unittest
from collections import deque

'''
cache implementation
'''

class LRUImageCache:

    def __init__(self, max_len: int) -> None:
        self.fp_set = set()
        self.fp_deque = deque(maxlen=max_len)
        #                   == deque ==
        # least recently used < --- > most recently used

    def move_to_end(self, index_to_move):
        if index_to_move < 0 or index_to_move >= len(self.fp_deque):
            raise IndexError("Index out of range for deque")
        
        # Rotate left to bring the element to leftmost position of deque
        self.fp_deque.rotate(-index_to_move)

        # Pop the element from left
        element_to_move = self.fp_deque.popleft()

        # rotate back so order is maintained
        self.fp_deque.rotate(index_to_move)

        # stick popped element on end
        self.fp_deque.append(element_to_move)

    def find_element(self, fp: str) -> int:
        for i in range(len(self.fp_deque) - 1, -1, -1):
            if self.fp_deque[i] == fp:
                return i
        return -1

    def lookup(self, fp: str) -> bool:
        if fp not in self.fp_set:
            # we need to add it to cache now

            # if queue is already full when we append the left element will be popped
            # we need to make sure the set is updated accordingly
            if len(self.fp_deque) == self.fp_deque.maxlen:
                self.fp_set.remove(self.fp_deque[0])

            # add to set and deque (adding to deque handles removal of leftmost element)
            self.fp_set.add(fp)
            self.fp_deque.append(fp)
            return False
        
        # doing this to ensure we are searching from the right to left because of this being a LRUCache        
        index = self.find_element(fp)
        # print(f'INDEX: {index}')
        
        # move fp to end of list since it's the most recently used
        self.move_to_end(index)

        # print(f'AFTER MOVE TO END {self.show()}')
        return True
    
    def show(self) -> str:
        return str(list(self.fp_deque))


class TestLRUImageCache(unittest.TestCase):
    def test_init(self):
        cache = LRUImageCache(5)
        self.assertEqual(len(cache.fp_deque), 0)
        self.assertEqual(len(cache.fp_set), 0)

    def test_lookup_hit(self):
        cache = LRUImageCache(5)
        cache.fp_set.add("img1")
        cache.fp_deque.append("img1")
        self.assertTrue(cache.lookup("img1"))
        self.assertEqual(cache.fp_deque[-1], "img1")

    def test_lookup_miss(self):
        cache = LRUImageCache(5)
        self.assertFalse(cache.lookup("img1"))
        self.assertIn("img1", cache.fp_set)
        self.assertEqual(cache.fp_deque[-1], "img1")

    def test_cache_full(self):
        cache = LRUImageCache(3)
        cache.fp_set.add("img1")
        cache.fp_deque.append("img1")
        cache.fp_set.add("img2")
        cache.fp_deque.append("img2")
        cache.fp_set.add("img3")
        cache.fp_deque.append("img3")
        self.assertFalse(cache.lookup("img4"))
        self.assertIn("img4", cache.fp_set)
        self.assertEqual(cache.fp_deque[-1], "img4")
        self.assertNotIn("img1", cache.fp_set)
        self.assertNotIn("img1", cache.fp_deque)

    def test_move_to_end(self):
        cache = LRUImageCache(5)
        cache.fp_deque.append("img1")
        cache.fp_deque.append("img2")
        cache.fp_deque.append("img3")
        cache.move_to_end(1)
        print(cache.show())
        self.assertEqual(cache.fp_deque[-1], "img2")
        self.assertEqual(cache.fp_deque[0], "img1")
        self.assertEqual(cache.fp_deque[1], "img3")

    def test_find_element(self):
        cache = LRUImageCache(5)
        cache.fp_deque.append("img1")
        cache.fp_deque.append("img2")
        cache.fp_deque.append("img3")
        self.assertEqual(cache.find_element("img2"), 1)
        self.assertEqual(cache.find_element("img4"), -1)

    def test_show(self):
        cache = LRUImageCache(5)
        cache.fp_deque.append("img1")
        cache.fp_deque.append("img2")
        cache.fp_deque.append("img3")
        self.assertEqual(cache.show(), "['img1', 'img2', 'img3']")

if __name__ == "__main__":
    unittest.main()

# if __name__ == '__main__':
#     test = [1, 2, 3, 1, 4, 5]

#     l = LRUImageCache(3)

#     for n in test:
#         l.lookup(n)
#         print(l.show())



