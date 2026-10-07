"""Create an empty project planning scope without inventing priorities or owners."""
import argparse
from pathlib import Path
from common import ROOT
from okf import write_directory_index
from project import project_dir


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id'); parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    try:
        target=project_dir(args.root,args.id)
        if target.exists(): raise ValueError('Refusing to overwrite project')
        content=(args.root/'vault/templates/project.md').read_text(encoding='utf-8').replace('{{PROJECT_ID}}',args.id)
        content=content.replace('../docs/project-workflow.md','../../docs/project-workflow.md')
        target.mkdir(parents=True)
        (target/'project.md').write_text(content,encoding='utf-8')
        write_directory_index(target,args.id); write_directory_index(target.parent,'專案與基準')
    except (OSError,ValueError) as exc:
        raise SystemExit(str(exc))
    print(f'Created {target}; define project scope before scheduling')


if __name__=='__main__': main()
