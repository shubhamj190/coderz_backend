import os

def print_directory_structure(root_dir, indent=""):
    exclude_dirs = {"venv", "node_modules"}  # Example set of directories to exclude
    entries = os.listdir(root_dir)
    for index, entry in enumerate(entries):
        if entry in exclude_dirs:
            continue

        path = os.path.join(root_dir, entry)
        if os.path.isdir(path):
            print(indent + "├── " + entry)
            print_directory_structure(path, indent + "│   ")
        else:
            print(indent + "└── " + entry)

print_directory_structure(".")