"""Create a blank OKF BRD and attachment folder without overwriting existing work."""
import argparse
from pathlib import Path
from brd import brd_directory
from common import ROOT
from okf import render_note, split_note, write_directory_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id')
    parser.add_argument('--title', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    target = brd_directory(args.root, args.id)
    if target.exists():
        raise SystemExit(f'Refusing to overwrite {args.id}')
    if not args.title.strip():
        raise SystemExit('BRD title must not be blank')
    metadata, body, _ = split_note((args.root/'vault/templates/brd.md').read_text(encoding='utf-8'))
    metadata.update(id=args.id, title=args.title)
    (target/'assets').mkdir(parents=True)
    (target/'brd.md').write_text(render_note(metadata, body), encoding='utf-8')
    (target/'assets/index.md').write_text('# BRD 附件\n\n放入原始圖片，並從 BRD 正文以相對連結引用。\n', encoding='utf-8')
    write_directory_index(target, args.id)
    write_directory_index(target.parent, '原始需求 BRD')
    print(f'Created {target}; write original items and add images before linking an assessment')


if __name__ == '__main__':
    main()
