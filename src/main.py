import sys

from generator import move_files, generate_pages_recursive

def main():
    basepath = sys.argv[0] or "/"
    move_files("static", "public")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()