from textnode import TextNode, TextType
from enum import Enum
import re

# Images: ![alt text](url)
image_pattern = re.compile(
    r"""
    !\[           # Literal '![' - start of image
    ([^\[\]]*)    # Capture group 1: alt text (any chars except brackets)
    \]            # Literal ']'
    \(            # Literal '('
    ([^\(\)]*)    # Capture group 2: URL (any chars except parens)
    \)            # Literal ')'
    """,
    re.VERBOSE
)

# Links: [anchor text](url) - but NOT images
link_pattern = re.compile(
    r"""
    (?<!\!)       # Negative lookbehind: not preceded by '!'
    \[            # Literal '['
    ([^\[\]]*)    # Capture group 1: anchor text
    \]            # Literal ']'
    \(            # Literal '('
    ([^\(\)]*)    # Capture group 2: URL
    \)            # Literal ')'
    """,
    re.VERBOSE
)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = []
    regex_delimiter = re.escape(delimiter)
    for node in old_nodes:
        if TextType.TEXT == node.text_type:
            
            matches = re.findall(rf"{regex_delimiter}", node.text)
            if len(matches) % 2 != 0:
                raise Exception(f"End delimiter '{delimiter}' not found in text: {node.text}")

            split_text = node.text.split(delimiter)
            if len(split_text) == 1:
                result.append(node)
                continue
           
            for i in range(len(split_text)):
                text = split_text[i]

                if text == "":
                    continue
                elif i % 2 == 0:
                    result.append(TextNode(text, TextType.TEXT))
                else:                    
                    result.append(TextNode(text, text_type))

        else:
            result.append(node)
    return result

def extract_markdown_images(text):
    return image_pattern.findall(text)

def extract_markdown_links(text):
    return link_pattern.findall(text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
            
        for image in images:
            alt_text = image[0]
            url = image[1]

            sections = original_text.split(f"![{alt_text}]({url})", 1)
            
            if len(sections) != 2:
                
                continue
            

            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            
            original_text = sections[1]
            
        
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
            
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
            
        for link in links:
            alt_text = link[0]
            url = link[1]
            
            sections = original_text.split(f"[{alt_text}]({url})", 1)
            
            if len(sections) != 2:
                
                continue
            
            
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            
            new_nodes.append(TextNode(alt_text, TextType.LINK, url))
            
            
            original_text = sections[1]
            
        
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
            
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    result = []
    for block in blocks:
        block = block.strip()
        if len(block) == 0:
            continue
        result.append(block)
    
    return result


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    QUOTE = "quote"
    CODE = "code"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    elif block.startswith("```\n") and block.endswith("\n```"):
        return BlockType.CODE
    elif block.startswith(">"):
        lines = block.split("\n")
        if all(line.startswith(">") for line in lines):
            return BlockType.QUOTE
        else:
            return BlockType.PARAGRAPH
    elif block.startswith("- "):
        lines = block.split("\n")
        if all(line.startswith("- ") for line in lines):
            return BlockType.UNORDERED_LIST
        else:            
            return BlockType.PARAGRAPH
    elif block.startswith("1. "):
        lines = block.split("\n")
        if all(line.startswith(f"{i}. ") for i, line in enumerate(lines, 1)):
            return BlockType.ORDERED_LIST
        else:            
            return BlockType.PARAGRAPH    
    else:
        return BlockType.PARAGRAPH
    
def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block[2:].strip()
    raise Exception("No title found in markdown")