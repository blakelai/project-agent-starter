"""Local BRD intake and provenance. Never interprets requirements or image content."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

from common import digest, index, load
from okf import check_note, split_note

BRD_ID = r'BRD-[A-Za-z0-9][A-Za-z0-9-]{0,63}'
ITEM_ID = r'br-[a-z0-9][a-z0-9-]{0,63}'


def brd_directory(root, identifier):
    if not re.fullmatch(BRD_ID, identifier):
        raise ValueError('BRD ID must match BRD-<letters/digits/hyphens>')
    return Path(root)/'vault/intake'/identifier


def visible_markdown(body):
    """Exclude comments and code from ID/image discovery; this is a bounded profile."""
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    lines, fence = [], None
    for line in body.splitlines():
        opening = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*', line):
                fence = None
            continue
        if opening:
            fence = opening.group(1)
            continue
        if line.startswith('    ') or line.startswith('\t'):
            continue
        lines.append(line)
    if fence:
        raise ValueError('Unclosed Markdown code fence in BRD')
    return re.sub(r'(`+).*?\1', '', '\n'.join(lines))


def manifest_revision(document):
    manifest = {'path': document['path'], 'sha256': document['sha256'],
                'assets': sorted([{'path': a['path'], 'sha256': a['sha256']}
                                  for a in document['assets']], key=lambda a: a['path'])}
    payload = json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return 'sha256:' + hashlib.sha256(payload).hexdigest()


def read_brd(root, source, allow_empty=False):
    root = Path(root).resolve()
    source = Path(source)
    path = (source if source.is_absolute() else root/source).resolve()
    intake = (root/'vault/intake').resolve()
    if not intake.is_relative_to(root) or not path.is_relative_to(intake) or path.name != 'brd.md' or path.parent.parent != intake:
        raise ValueError('BRD must be vault/intake/<BRD-ID>/brd.md')
    check_note(path, root/'vault')
    metadata, body, _ = split_note(path.read_text(encoding='utf-8'))
    identifier = metadata.get('id')
    if not isinstance(identifier, str) or not re.fullmatch(BRD_ID, identifier) or identifier != path.parent.name:
        raise ValueError('BRD frontmatter id must match its BRD directory')
    if metadata.get('type') != 'Business Requirements Document' or not metadata.get('title'):
        raise ValueError('BRD needs type: Business Requirements Document and a title')
    visible = visible_markdown(body)
    items = []
    for heading in re.findall(r'^##\s+(.+?)\s*$', visible, flags=re.MULTILINE):
        if heading.lower().startswith('br-'):
            if not re.fullmatch(ITEM_ID, heading):
                raise ValueError('Use a standalone lowercase ## br-001 heading; put the title on the next line')
            items.append(heading)
    if len(items) != len(set(items)):
        raise ValueError('Duplicate BRD item ID')
    if not items and not allow_empty:
        raise ValueError('BRD has no requirement items; add ## br-001 headings before import')

    assets = {}
    pattern = r'!\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)'
    for match in re.finditer(pattern, visible):
        destination = match.group(1).strip()
        if destination.startswith('<') and destination.endswith('>'):
            destination = destination[1:-1]
        else:
            match_url = re.fullmatch(r'''(\S+?)(?:\s+["'][^"']*["'])?''', destination)
            if not match_url:
                raise ValueError('Use URL-encoded spaces in Markdown image paths')
            destination = match_url.group(1)
        url = urlsplit(destination)
        if url.scheme or url.netloc or url.query or not url.path or Path(unquote(url.path)).is_absolute():
            raise ValueError('BRD images must be local files under its assets/ directory')
        asset = (path.parent/unquote(url.path)).resolve()
        asset_root = (path.parent/'assets').resolve()
        if not asset_root.is_relative_to(path.parent) or not asset.is_relative_to(asset_root) or not asset.is_file():
            raise ValueError(f'Missing or out-of-bounds BRD image: {destination}')
        relative = asset.relative_to(root).as_posix()
        assets[relative] = {'path': relative, 'sha256': digest(asset), 'review_status': 'pending',
                            'reviewed_by': None, 'reviewed_at': None, 'notes': None, 'question_ids': []}
    # Do not silently miss Obsidian embeds, reference-style images or raw HTML images.
    remainder = re.sub(pattern, '', visible)
    if re.search(r'!\[|<img\b|<picture\b|<svg\b', remainder, flags=re.IGNORECASE):
        raise ValueError('Use inline Markdown images: ![caption](assets/file.png)')
    result = {'id': identifier, 'path': path.relative_to(root).as_posix(), 'title': metadata['title'],
              'sha256': digest(path), 'item_ids': items, 'assets': list(assets.values())}
    result['source_revision'] = manifest_revision(result)
    return result


def capture_brd(root, source):
    result = read_brd(root, source)
    result['captured_at'] = datetime.now(timezone.utc).isoformat()
    result['git_commit'] = None
    try:
        proc = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel', 'HEAD'],
                              capture_output=True, text=True)
    except FileNotFoundError:
        return result
    lines = proc.stdout.splitlines()
    if proc.returncode == 0 and len(lines) == 2 and Path(lines[0]).resolve() == Path(root).resolve():
        result['git_commit'] = lines[1]
    return result


def registered_sources(root, documents):
    """Prepare a registry update without writing files or replacing existing entries."""
    registry = load(Path(root)/'vault/knowledge/sources.md')
    known = index(registry['sources'], 'sources')
    for doc in documents:
        entry = {'id': doc['id'], 'kind': 'brd', 'path': doc['path']}
        if doc['id'] in known:
            if any(known[doc['id']].get(k) != v for k, v in entry.items()):
                raise ValueError(f'{doc["id"]}: source registry ID/path conflict')
        else:
            registry['sources'].append(entry)
            known[doc['id']] = entry
    return registry


def pending_coverage(documents):
    return [{'document_id': doc['id'], 'item_id': item, 'disposition': 'pending',
             'functional_requirement_ids': [], 'question_ids': [], 'reason': None, 'decision_ref': None}
            for doc in documents for item in doc['item_ids']]


def validate_brd_references(root, req, traceability, questions, ready=False):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    try:
        documents = req.get('source_documents', [])
        if not isinstance(documents, list):
            raise ValueError('source_documents must be a list')
        docs = index(documents, 'source_documents')
        registry = index(load(Path(root)/'vault/knowledge/sources.md')['sources'], 'sources')
        expected = set()
        for doc in documents:
            current = read_brd(root, doc['path'])
            require(doc['id'] == current['id'], 'BRD ID/path mismatch')
            registered = registry.get(doc['id'], {})
            require(registered.get('kind') == 'brd' and registered.get('path') == doc['path'],
                    f'{doc["id"]}: BRD not registered at this path')
            require(doc['source_revision'] == manifest_revision(doc), f'{doc["id"]}: inconsistent BRD snapshot')
            require(doc['source_revision'] == current['source_revision'],
                    f'{doc["id"]}: BRD or attachment changed; refresh sources and reassess')
            require(doc['item_ids'] == current['item_ids'], f'{doc["id"]}: BRD item inventory changed')
            require(bool(doc.get('captured_at')), f'{doc["id"]}: missing captured_at')
            expected.update((doc['id'], item) for item in current['item_ids'])
            for asset in doc['assets']:
                state = asset['review_status']
                require(state in {'pending','reviewed','unreadable'}, f'{asset["path"]}: invalid image review status')
                if state == 'reviewed':
                    require(bool(asset.get('reviewed_by')) and bool(asset.get('reviewed_at')) and bool(asset.get('notes')),
                            f'{asset["path"]}: image review needs reviewer, time and observations')
                if state == 'unreadable':
                    require(bool(asset.get('notes')) and bool(asset.get('question_ids')),
                            f'{asset["path"]}: unreadable image needs reason and question IDs')
                require(set(asset.get('question_ids', [])) <= questions.keys(), f'{asset["path"]}: unknown image question')
                if ready:
                    require(state == 'reviewed', f'{asset["path"]}: image not reviewed; cannot plan')

        forward = {key: set() for key in expected}
        for fr in req['functional_requirements']:
            refs = fr.get('source_refs', [])
            if docs:
                require(bool(refs), f'{fr["id"]}: missing BRD source_refs')
            seen_refs = set()
            for ref in refs:
                key = (ref['document_id'], ref['item_id'])
                require(key in expected, f'{fr["id"]}: unknown BRD item {key}')
                require(key not in seen_refs, f'{fr["id"]}: duplicate BRD reference')
                seen_refs.add(key)
                if key in forward:
                    forward[key].add(fr['id'])
        seen = set()
        for row in traceability.get('source_coverage', []):
            key = (row['document_id'], row['item_id'])
            require(key in expected and key not in seen, f'Unknown or duplicate BRD coverage: {key}')
            seen.add(key)
            disposition = row['disposition']
            require(disposition in {'pending','analyzed','needs-clarification','deferred','excluded'},
                    f'{key}: invalid BRD disposition')
            ids = row['functional_requirement_ids']
            require(isinstance(ids, list) and len(ids) == len(set(ids)), f'{key}: invalid FR coverage IDs')
            require(set(ids) == forward.get(key, set()), f'{key}: BRD coverage differs from FR source_refs')
            require(set(row.get('question_ids', [])) <= questions.keys(), f'{key}: unknown clarification question')
            if disposition == 'analyzed':
                require(bool(ids), f'{key}: analyzed item needs FR mapping')
            if disposition == 'needs-clarification':
                require(bool(row.get('question_ids')), f'{key}: needs clarification question IDs')
            if disposition in {'deferred','excluded'}:
                require(bool(row.get('reason')) and not ids, f'{key}: deferred/excluded item needs reason and no FR mapping')
                if ready:
                    require(bool(row.get('decision_ref')), f'{key}: deferred/excluded scope needs decision_ref before planning')
            if ready:
                require(disposition not in {'pending','needs-clarification'}, f'{key}: unresolved BRD coverage blocks planning')
        require(seen == expected, 'BRD source_coverage must account for every original item exactly once')
    except (OSError, KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append(f'Malformed BRD reference: {exc}')
    return errors
