import os
import json

def get_structure(startpath):
    structure = []
    # Directories to ignore
    ignore_dirs = {'.git', '.github', 'scratch', 'node_modules'}
    
    for root, dirs, files in os.walk(startpath):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        # We only care about markdown files
        md_files = [f for f in files if f.endswith('.md') and f.lower() != 'readme.md']
        
        # Always include README if it's in the current folder (except root which we handle specially)
        all_files = md_files
        if 'README.md' in files and root != startpath:
            all_files.append('README.md')
            
        rel_path = os.path.relpath(root, startpath)
        if rel_path == ".":
            rel_path = ""
            # In root, we specifically want to include README.md as the first item
            if 'README.md' in files:
                md_files.insert(0, 'README.md')
            
        if md_files:
            folder_node = {
                "name": os.path.basename(root) if rel_path else "Home",
                "path": rel_path,
                "files": [{"name": f, "path": os.path.join(rel_path, f).replace('\\', '/')} for f in md_files],
                "is_root": rel_path == ""
            }
            structure.append(folder_node)
    
    # Sort: Root first, then alphabetical by path
    structure.sort(key=lambda x: (not x['is_root'], x['path']))
    return structure

if __name__ == "__main__":
    # Use current directory
    repo_path = os.getcwd()
    data = get_structure(repo_path)
    with open("structure.json", "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ structure.json updated successfully!")
