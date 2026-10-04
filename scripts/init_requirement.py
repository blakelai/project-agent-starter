"""Create an intake from templates without overwriting an existing requirement."""
import argparse
import shutil
from pathlib import Path
from common import ROOT, requirement_dir

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id'); parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args(); target=requirement_dir(args.root,args.id)
    if target.exists(): raise SystemExit(f'Refusing to overwrite {args.id}')
    shutil.copytree(args.root/'templates/requirement',target)
    for path in target.rglob('*'):
        if path.is_file(): path.write_text(path.read_text(encoding='utf-8').replace('{{REQ_ID}}',args.id),encoding='utf-8')
    print(f'Created intake {args.id}; resolve scope/evidence before assessment or scheduling')
if __name__=='__main__': main()
