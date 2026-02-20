import os, shutil
from md_to_html import markdown_to_html_node
from md_to_text import extract_title

def move_files(src_dir, dest_dir):
    dest_folder = os.path.abspath(dest_dir)

    try:
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder)
        else:
            os.makedirs(dest_folder)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (dest_folder, e))

    src_folder = os.path.abspath(src_dir)
    for filename in os.listdir(src_folder):
        src_file_path = os.path.join(src_folder, filename)
        dest_file_path = os.path.join(dest_folder, filename)
        try:
            if os.path.isfile(src_file_path):
                shutil.copy2(src_file_path, dest_file_path)
            elif os.path.isdir(src_file_path):
                shutil.copytree(src_file_path, dest_file_path)
        except Exception as e:
            print('Failed to copy %s. Reason: %s' % (src_file_path, e))

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    md_file = None
    from_path = os.path.abspath(from_path)
    if os.path.isdir(from_path):
        for filename in os.listdir(from_path):
            if os.path.isfile(os.path.join(from_path, filename)) and filename.endswith(".md"):
               md_file = os.path.join(from_path, filename)
               break
    else:
        md_file = from_path

    if md_file is None:
        raise Exception(f"No markdown file found in directory: {from_path}")

    with open(md_file, "r") as f:
        md_content = f.read()

    template_file = None
    template_path = os.path.abspath(template_path)
    if os.path.isdir(template_path):
        for filename in os.listdir(template_path):
            if os.path.isfile(os.path.join(template_path, filename)) and filename.endswith(".html"):
               template_file = os.path.join(template_path, filename)
               break
    else:
        template_file = template_path

    if template_file is None:
        raise Exception(f"No template file found in directory: {template_path}")
    
    with open(template_file, "r") as f:
        template_content = f.read()

    #print(f"Markdown content:\n{md_content}\n")
    html_node = markdown_to_html_node(md_content)
    html_content = html_node.to_html()


    title = extract_title(md_content)

    template_content = template_content.replace("{{ Content }}", html_content)
    template_content = template_content.replace("{{ Title }}", title)

    print(f"using basepath: {basepath}")
    template_content = template_content.replace("href:\"/", f"href:\"{basepath}")
    template_content = template_content.replace("src:\"/", f"src:\"{basepath}")

    dest_path = os.path.abspath(dest_path)
    if os.path.isdir(dest_path):
        dest_file_path = os.path.join(dest_path, "index.html")
    else:
        dest_file_path = dest_path
    
    with open(dest_file_path, "w") as f:
        f.write(template_content)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    dir_path_content = os.path.abspath(dir_path_content)
    template_path = os.path.abspath(template_path)
    dest_dir_path = os.path.abspath(dest_dir_path)

    for filename in os.listdir(dir_path_content):
        content_file_path = os.path.join(dir_path_content, filename)
        if os.path.isfile(content_file_path) and filename.endswith(".md"):
            generate_page(content_file_path, template_path, dest_dir_path, basepath)
        elif os.path.isdir(content_file_path):
            new_dest_dir_path = os.path.join(dest_dir_path, filename)
            os.makedirs(new_dest_dir_path, exist_ok=True)
            generate_pages_recursive(content_file_path, template_path, new_dest_dir_path, basepath)