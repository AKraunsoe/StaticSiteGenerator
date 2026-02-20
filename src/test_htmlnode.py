import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, ParentNode


class TestHtmlNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "Hello World", [], {"class": "text"})
        node2 = HTMLNode("p", "Hello World", [], {"class": "text"})
        self.assertEqual(node, node2)

    def test_neq(self):
        node = HTMLNode(tag="p", value="Hello World", props={"class": "text"})
        node2 = HTMLNode(tag="p", value="Hello World", props={"class": "different"})
        self.assertNotEqual(node, node2)

    def test_repr(self):
        node = HTMLNode(tag="p", value="Hello World", props={"class": "text"})
        self.assertEqual(repr(node), "HTMLNode(p, Hello World, [],  class=\"text\")")
    
    def test_props_to_html(self):
        node = HTMLNode(tag="p", value="Hello World", props={"class": "text", "id": "paragraph"})
        self.assertEqual(node.props_to_html(), ' class="text" id="paragraph"')

    def test_empty_props_to_html(self):
        node = HTMLNode(tag="p", value="Hello World")
        self.assertEqual(node.props_to_html(), '')

    def test_to_html_not_implemented(self):
        node = HTMLNode(tag="p", value="Hello World")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just some text")
        self.assertEqual(node.to_html(), "Just some text")

    def test_leaf_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_repr(self):
        node = LeafNode("p", "Hello, world!", {"class": "text"})
        self.assertEqual(repr(node), "LeafNode(p, Hello, world!,  class=\"text\")")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_to_html_parent_no_tag(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_parent_child_no_value(self):
        child_node = LeafNode("span", None)
        parent_node = ParentNode("div", [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()
    
    def test_to_html_parent_child_not_htmlnode(self):
        parent_node = ParentNode("div", ["not a html node"])
        with self.assertRaises(ValueError):
            parent_node.to_html()   
    
    def test_to_html_parent_no_children(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_image(self):
        node = LeafNode("img", "", {"src": "/images/tolkien.png", "alt": "JRR Tolkien sitting"})
        self.assertEqual(node.to_html(), '<img src="/images/tolkien.png" alt="JRR Tolkien sitting"></img>')

if __name__ == "__main__":
    unittest.main()