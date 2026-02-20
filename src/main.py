import sys

from generator import move_files, generate_pages_recursive

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    move_files("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()