import unittest

from textnode import TextNode, TextType
from md_to_text import BlockType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, extract_title


class TestTextNode(unittest.TestCase):
    def test_one_node(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT)
        ])
    
    def test_incomplete_delimiter(self):
        node = TextNode("This is text with an `incomplete code block word", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertTrue("End delimiter '`' not found in text: This is text with an `incomplete code block word" in str(context.exception))

    def test_no_delimiter(self):
        node = TextNode("This is text with no code block word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [node])

    def test_multiple_delimiters(self):
        node = TextNode("This is `code` with multiple `code blocks` in one `line`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" with multiple ", TextType.TEXT),
            TextNode("code blocks", TextType.CODE),
            TextNode(" in one ", TextType.TEXT),
            TextNode("line", TextType.CODE)
        ])
    
    def test_multiple_delimiters_no_end(self):
        node = TextNode("This is `code` with multiple `code blocks` in one `line", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertTrue("End delimiter '`' not found in text: This is `code` with multiple `code blocks` in one `line" in str(context.exception))

    def test_bold_delimiter_types(self):
        node = TextNode("This is **bold** with multiple **code blocks** in one line", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" with multiple ", TextType.TEXT),
            TextNode("code blocks", TextType.BOLD),
            TextNode(" in one line", TextType.TEXT)
        ])
    
    def test_empty_string(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [node])

    def test_delimiter_at_start_and_end(self):
        node = TextNode("`code at start and end`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("code at start and end", TextType.CODE)
        ])
    
    def test_consecutive_delimiters(self):
        node = TextNode("This is ``consecutive delimiters`` test", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("consecutive delimiters", TextType.TEXT),
            TextNode(" test", TextType.TEXT)
        ])

    def test_delimiter_as_end(self):
        node = TextNode("This is a test with empty `code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is a test with empty ", TextType.TEXT),
            TextNode("code block", TextType.CODE)
        ])
    
    def test_delimiter_as_start(self):
        node = TextNode("_code block_ is at the start of this text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(new_nodes, [
            TextNode("code block", TextType.ITALIC),
            TextNode(" is at the start of this text", TextType.TEXT)
        ])
    
    def test_delimiter_with_only_delimiter(self):
        node = TextNode("`code block only delimiter`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("code block only delimiter", TextType.CODE)
        ])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![image2](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png"), ("image2", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_no_match(self):
        matches = extract_markdown_images(
            "This is text with no images"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev)"
        )
        self.assertListEqual([("link", "https://boot.dev")], matches)
    
    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and another [link2](https://boot.dev)"
        )
        self.assertListEqual([("link", "https://boot.dev"), ("link2", "https://boot.dev")], matches)

    def test_extract_markdown_links_no_match(self):
        matches = extract_markdown_links(
            "This is text with no links"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_links_with_images_link(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("link", "https://boot.dev")], matches)

    def test_extract_markdown_links_with_images_image(self):
        matches = extract_markdown_images(
            "This is text with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and another [second link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://boot.dev"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links_with_images(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and an ![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT)
            ],
            new_nodes,
        )

    def test_split_images_with_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with a [link](https://boot.dev) and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")
            ],
            new_nodes,
        )

    def test_split_images_with_no_images(self):
        node = TextNode(
            "This is text with no images [link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with no images [link](https://boot.dev)", TextType.TEXT)
            ],
            new_nodes,
        )

    def test_split_links_with_no_links(self):
        node = TextNode(
            "This is text with no links ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with no links ![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT)
            ],
            new_nodes,
        )
    
    def test_split_images_and_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image(split_nodes_link([node]))
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev")
            ],
            nodes,
        )

    def test_text_to_textnodes_with_no_markdown(self):
        text = "This is text with no markdown"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is text with no markdown", TextType.TEXT)
            ],
            nodes,
        )

    def test_text_to_textnodes_with_some_markdown(self):
        text = "**bold** and _italic_ and ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg")
            ],
            nodes,
        )

    def test_markdown_to_blocks(self):
        md = """
            This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
            """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_with_empty_lines(self):
        md = """
            This is **bolded** paragraph
This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line





- This is a list
- with items
            
            
            
            
            """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph\nThis is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_with_only_empty_lines(self):
        md = """


        
        
        """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [],
        )
    
    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)

    def test_block_to_block_type_fake_heading(self):
        self.assertEqual(block_to_block_type("####### Not a heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("##Heading without space"), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">This is a quote\n> on multiple lines"), BlockType.QUOTE)

    def test_block_to_block_type_fake_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote\nNot a quote"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("This is not a quote\n> But this is a quote"), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2\n- Item 3"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_fake_unordered_list(self):
        self.assertEqual(block_to_block_type("- Item 1\nNot a list item"), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2\n3. Item 3"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_fake_ordered_list(self):
        self.assertEqual(block_to_block_type("1. Item 1\n- Not a list item"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1. Item 1\n3. Not a list item"), BlockType.PARAGRAPH)

    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```\nCode block\n```"), BlockType.CODE)

    def test_block_to_block_type_fake_code(self):
        self.assertEqual(block_to_block_type("```\nCode block without end"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("Code block without start\n```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```Code block without end```"), BlockType.PARAGRAPH)

    def test_block_to_block_type(self):
        
        self.assertEqual(block_to_block_type("```\nCode block without end"), BlockType.PARAGRAPH)

    def extract_title(self):
        md = """
# This is the title
This is a paragraph with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)
        """
        title = extract_title(md)
        self.assertEqual(title, "This is the title")
    
    def extract_title_no_title(self):
        md = """
This is a paragraph with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)
        """
        with self.assertRaises(Exception) as context:
            extract_title(md)
        self.assertTrue("No title found in markdown" in str(context.exception))
    
    def extract_title_with_fake_title(self):
        md = """
#### Not a title
This is a paragraph with a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)
        """
        with self.assertRaises(Exception) as context:
            extract_title(md)
        self.assertTrue("No title found in markdown" in str(context.exception))

if __name__ == "__main__":
    unittest.main()