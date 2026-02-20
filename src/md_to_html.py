from md_to_text import markdown_to_blocks, block_to_block_type, BlockType, text_to_textnodes
from textnode import text_node_to_html_node, TextNode, TextType
from htmlnode import ParentNode
import re

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.HEADING:
                text_nodes = text_to_textnodes(re.sub(r"^#+ ", "", block))
                node = ParentNode(f"h{block.count('#')}", text_to_children(text_nodes))
                html_nodes.append(node)
            case BlockType.PARAGRAPH:
                text_nodes = text_to_textnodes(block.replace("\n", " "))
                html_node = ParentNode("p", text_to_children(text_nodes))
                html_nodes.append(html_node)
            case BlockType.QUOTE:
                text_nodes = text_to_textnodes(re.sub(r"^>[ ]?", "", block, flags=re.MULTILINE).replace("\n", " "))
                node = ParentNode("blockquote", text_to_children(text_nodes))
                html_nodes.append(node)
            case BlockType.ORDERED_LIST:
                list_items = block.split("\n")
                list_nodes = []
                for i, item in enumerate(list_items, 1):
                    item = re.sub(r"^\d+\. ", "", item, count=1)
                    text_nodes = text_to_textnodes(item)
                    html_node = ParentNode("li", text_to_children(text_nodes))
                    list_nodes.append(html_node)
                parent_node = ParentNode("ol", list_nodes)
                html_nodes.append(parent_node)
            case BlockType.UNORDERED_LIST:
                list_items = block.split("\n")
                list_nodes = []
                for item in list_items:
                    item = re.sub(r"^- ", "", item, count=1)
                    text_nodes = text_to_textnodes(item)
                    html_node =  ParentNode("li", text_to_children(text_nodes))
                    list_nodes.append(html_node)
                parent_node = ParentNode("ul", list_nodes)
                html_nodes.append(parent_node)
            case BlockType.CODE:
                text_node = TextNode(block.strip("```").lstrip("\n"), TextType.CODE)
                node = ParentNode("pre", [text_node_to_html_node(text_node)])
                html_nodes.append(node)
            case _:
                raise ValueError(f"Unsupported block type: {block_type}")
            

    parent_node = ParentNode("div", html_nodes)
    return parent_node

def text_to_children(nodes):
    return  [text_node_to_html_node(node) for node in nodes]