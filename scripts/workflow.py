"""Materialize phase artifacts without overwriting content or claiming phase completion."""
import argparse
from pathlib import Path
import shutil

from common import ROOT, load, requirement_dir
from okf import write_directory_index

CORE = ['requirement.md', 'evidence.md', 'assessment.md', 'traceability.md']
FILES = {
    'intake': CORE,
    'solution': CORE + ['solution-assessment.md'],
    'planning': CORE + ['work-breakdown.md', 'estimation.md', 'risks.md', 'project-plan.md', 'assessment-review.md'],
    'delivery': CORE + ['work-breakdown.md', 'estimation.md', 'risks.md', 'project-plan.md', 'assessment-review.md',
                        'progress.md', 'backlog-handoff.md'],
}
PHASES = ['intake', 'requirements', 'planning', 'delivery', 'closure']
STATUS_PHASE = {'intake': 'intake', 'clarified': 'requirements', 'assessed': 'planning',
                'baseline': 'planning', 'in-progress': 'delivery', 'closed': 'closure'}


def materialize(root, identifier, phase='intake'):
    root = Path(root).resolve(); target = requirement_dir(root, identifier)
    if target.resolve() != target:
        raise ValueError('Requirement path must not traverse symlinks')
    if (target/'requirement.md').exists():
        req = load(target/'requirement.md')
        if req['status'] == 'closed':
            raise ValueError('Cannot prepare artifacts in a closed requirement')
    template = root/'vault/templates/requirement'
    contents = {name: (template/name).read_text(encoding='utf-8').replace('{{REQ_ID}}', identifier)
                for name in FILES[phase] if not (target/name).exists()}
    target.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        (target/name).write_text(content, encoding='utf-8')
    # Binary template assets are never read as text and existing attachments are preserved.
    if (template/'assets').exists():
        for source in (template/'assets').rglob('*'):
            if source.is_file():
                destination = target/source.relative_to(template)
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
    write_directory_index(target, identifier)
    write_directory_index(target.parent, '需求')
    return sorted(contents)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--requirement', required=True)
    parser.add_argument('--stage', choices=FILES, required=True)
    args = parser.parse_args()
    if not requirement_dir(args.root, args.requirement).exists():
        raise SystemExit('Initialize the requirement with init_requirement.py first')
    try:
        print('Created: ' + ', '.join(materialize(args.root, args.requirement, args.stage)))
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc))


if __name__ == '__main__':
    main()
