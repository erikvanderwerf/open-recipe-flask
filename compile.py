import os
import tarfile

MUTABLE = 'mutable'
ORF_DIR = os.path.join('serve', 'orf')

os.makedirs(ORF_DIR, exist_ok=True)

for filename in os.listdir(MUTABLE):
    src = os.path.join(MUTABLE, filename)
    dst = os.path.join(ORF_DIR, f'root.{filename}.1.orf')
    with tarfile.open(dst, 'w:gz') as tar:
        for inner in os.listdir(src):
            item = os.path.join(src, inner)
            tar.add(item, arcname=inner)
