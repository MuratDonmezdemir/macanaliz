import re

# Read the file
with open("app/models/league.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the CheckConstraint lines
content = re.sub(
    r"db\.CheckConstraint\(\"([^\"]*)\"\s*,\s*name='([^']*)'\)",
    r'db.CheckConstraint("\1", name="\2")',
    content,
)

# Write the fixed content back to the file
with open("app/models/league.py", "w", encoding="utf-8") as f:
    f.write(content)

print("File has been fixed successfully!")
