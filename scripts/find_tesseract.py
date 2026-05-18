import os
import sys

search_paths = [
    os.environ.get('ProgramFiles', r'C:\Program Files'),
    os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
    r'C:\ProgramData',
]

matches = []
for base in search_paths:
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower() == 'tesseract.exe':
                matches.append(os.path.join(root, f))

if not matches:
    print('NOTFOUND')
    sys.exit(0)

# Print all found, one per line
for m in matches:
    print(m)
