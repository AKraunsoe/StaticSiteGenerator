from generator import move_files, generate_page, generate_pages_recursive
import textnode

def main():
    move_files("static", "public")
    generate_pages_recursive("content", "template.html", "public")

main()