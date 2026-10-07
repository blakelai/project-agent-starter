"""Recapture changed BRD inputs and invalidate draft readiness without erasing analysis."""
import argparse
from pathlib import Path
from brd import capture_brd, pending_coverage, registered_sources
from common import ROOT, load, write, requirement_dir


def refresh(root, directory):
    req = load(directory/'requirement.md')
    assess = load(directory/'assessment.md')
    trace = load(directory/'traceability.md')
    if req['status'] in {'baseline','closed'} or assess['status'] == 'baseline':
        raise ValueError('Cannot refresh baseline/closed requirements; create an authorized change assessment')
    documents = req.get('source_documents', [])
    changed, updated = set(), []
    for old in documents:
        new = capture_brd(root, old['path'])
        if old['id'] != new['id']:
            raise ValueError('BRD identity changed; preserve the original document ID')
        if old['source_revision'] == new['source_revision']:
            updated.append(old)
            continue
        changed.add(old['id'])
        prior_assets = {a['path']: a for a in old['assets']}
        new['assets'] = [{**prior_assets.get(a['path'], {}), **a} for a in new['assets']]
        updated.append({**old, **new})
    if not changed:
        return []
    registry = registered_sources(root, updated)
    rows = trace.setdefault('source_coverage', [])
    known = {(r['document_id'], r['item_id']) for r in rows}
    for row in rows:
        if row['document_id'] in changed:
            row.update(disposition='pending', decision_ref=None)
    for row in pending_coverage(updated):
        if (row['document_id'], row['item_id']) not in known:
            rows.append(row)
    # Retain removed-item rows and FR/evidence references: the reviewer must resolve them explicitly.
    req.update(source_documents=updated, status='intake')
    assess.update(ready_for_planning=False, reviewed_by=None, reviewed_at=None, owner_confirmation=None)
    assess.setdefault('blockers', []).append('BRD sources changed; reassess coverage, images and evidence: ' + ', '.join(sorted(changed)))
    write(directory/'requirement.md', req)
    write(directory/'traceability.md', trace)
    write(directory/'assessment.md', assess)
    write(root/'vault/knowledge/sources.md', registry)
    return sorted(changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--requirement', required=True)
    args = parser.parse_args()
    try:
        changed = refresh(args.root, requirement_dir(args.root, args.requirement))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(str(exc))
    print('Refreshed: ' + ', '.join(changed) if changed else 'BRD inputs unchanged')


if __name__ == '__main__':
    main()
