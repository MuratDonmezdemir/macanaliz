def fix_encoding(file_path):
    # Read the file with error handling for encoding
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    # Replace Turkish characters in docstrings and comments
    replacements = {
        "Kazanan takımın ID'sini döndürür": "Returns the ID of the winning team",
        "Kaybeden takımın ID'sini döndürür": "Returns the ID of the losing team",
        # Add more replacements as needed
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Write the fixed content back to the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("File encoding fixed successfully!")
    except Exception as e:
        print(f"Error writing file: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        fix_encoding(sys.argv[1])
    else:
        fix_encoding("app/models/match.py")
