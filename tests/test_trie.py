import random

from src.core.geohash import encode
from src.core.trie import CompactTrie


def test_empty_trie():
    trie = CompactTrie()
    assert trie.search("") == []
    assert trie.search("abc") == []


def test_insert_and_search_prefix():
    trie = CompactTrie()
    trie.insert("7h2wj", "a")
    trie.insert("7h2wm", "b")
    trie.insert("7h2x0", "c")
    trie.insert("6gyf4", "d")

    assert sorted(trie.search("")) == ["a", "b", "c", "d"]
    assert sorted(trie.search("7h2")) == ["a", "b", "c"]
    assert sorted(trie.search("7h2w")) == ["a", "b"]
    assert trie.search("7h2wj") == ["a"]
    assert trie.search("6") == ["d"]
    assert trie.search("7h3") == []
    assert trie.search("7h2wjz") == []


def test_prefix_ending_inside_edge():
    trie = CompactTrie()
    trie.insert("7h2wjkp", "a")
    assert trie.search("7h2w") == ["a"]
    assert trie.search("7h2x") == []


def test_key_that_is_prefix_of_another():
    trie = CompactTrie()
    trie.insert("7h2wjkp", "long")
    trie.insert("7h2", "short")
    assert sorted(trie.search("7h2")) == ["long", "short"]
    assert trie.search("7h2w") == ["long"]


def test_same_key_stack_values():
    trie = CompactTrie()
    trie.insert("7h2wj", "a")
    trie.insert("7h2wj", "b")
    assert sorted(trie.search("7h2wj")) == ["a", "b"]
