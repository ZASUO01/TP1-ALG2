class Node:
    def __init__(self, label=""):
        self.label = label
        self.children = {}
        self.values = []


def commonPrefixLength(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


class CompactTrie:
    def __init__(self):
        self.root = Node()

    def insert(self, key, value):
        node = self.root
        i = 0
        while i < len(key):
            child = node.children.get(key[i])
            if child is None:
                leaf = Node(key[i:])
                leaf.values.append(value)
                node.children[key[i]] = leaf
                return

            common = commonPrefixLength(child.label, key[i:])
            if common < len(child.label):
                middle = Node(child.label[:common])
                child.label = child.label[common:]
                middle.children[child.label[0]] = child
                node.children[key[i]] = middle
                child = middle

            node = child
            i += common
        node.values.append(value)

    def search(self, prefix):
        node = self.root
        i = 0
        while i < len(prefix):
            child = node.children.get(prefix[i])
            if child is None:
                return []

            common = commonPrefixLength(child.label, prefix[i:])
            if common == len(prefix) - i:
                return self.collect(child)
            if common < len(child.label):
                return []

            node = child
            i += common
        return self.collect(node)

    def collect(self, node):
        result = []
        stack = [node]
        while stack:
            current = stack.pop()
            result.extend(current.values)
            stack.extend(current.children.values())
        return result
