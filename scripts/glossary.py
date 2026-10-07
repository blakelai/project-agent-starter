"""Domain vocabulary records, revision checks and assessment gates; no semantic inference."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit

from brd import visible_markdown
from common import digest, index, load
from okf import check_note, split_note

TERM_ID = r'TERM-[A-Za-z0-9][A-Za-z0-9-]{0,63}'
CONTEXT_ID = r'CTX-[A-Za-z0-9][A-Za-z0-9-]{0,63}'
START = '<!-- term-definition:start -->'
END = '<!-- term-definition:end -->'


def text(value):
    return isinstance(value, str) and bool(value.strip())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def records(value, label):
    require(isinstance(value, list), f'{label}: expected list')
    return index(value, label)


def timestamp(value):
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'Timestamp needs an explicit UTC offset')


def revision(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')
    return 'sha256:' + hashlib.sha256(payload).hexdigest()


def glossary_dir(root):
    root = Path(root).resolve()
    path = root/'vault/knowledge/glossary'
    require(path.resolve() == path, 'Glossary path must not traverse symlinks')
    return path


def term_path(root, identifier):
    require(isinstance(identifier, str) and re.fullmatch(TERM_ID, identifier), 'Invalid TERM ID')
    path = glossary_dir(root)/(identifier + '.md')
    require(path.resolve() == path, 'Term path must not traverse symlinks')
    return path


def contexts(root):
    path = glossary_dir(root)/'contexts.md'
    require(path.resolve() == path, 'Context path must not traverse symlinks')
    result = records(load(path)['contexts'], 'contexts')
    for identifier, ctx in result.items():
        require(re.fullmatch(CONTEXT_ID, identifier) and text(ctx.get('name')) and text(ctx.get('definition')),
                f'{identifier}: context needs CTX ID, name and definition')
    return result


def definition_assets(root, path, definition):
    """Support only local inline images, with the same bounded Markdown syntax as BRD intake."""
    visible = visible_markdown(definition)
    pattern = r'!\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)'
    assets = {}
    for match in re.finditer(pattern, visible):
        destination = match.group(1).strip()
        if destination.startswith('<') and destination.endswith('>'):
            destination = destination[1:-1]
        else:
            parsed = re.fullmatch(r'''(\S+?)(?:\s+["'][^"']*["'])?''', destination)
            require(parsed is not None, 'Use URL-encoded spaces in image paths')
            destination = parsed.group(1)
        url = urlsplit(destination)
        require(not (url.scheme or url.netloc or url.query) and url.path and
                not Path(unquote(url.path)).is_absolute(), 'Term images must be local assets')
        boundary = path.parent/'assets'/path.stem
        asset = (path.parent/unquote(url.path)).resolve()
        require(boundary.resolve() == boundary and asset.is_relative_to(boundary) and asset.is_file(),
                'Missing or out-of-bounds term image')
        key = asset.relative_to(Path(root).resolve()).as_posix()
        assets[key] = {'path': key, 'sha256': digest(asset)}
    require(not re.search(r'!\[|<img\b|<picture\b|<svg\b', re.sub(pattern, '', visible), re.I),
            'Use inline Markdown images under assets/<TERM-ID>/')
    return sorted(assets.values(), key=lambda a: a['path'])


def read_term(root, identifier):
    path = term_path(root, identifier)
    check_note(path, Path(root).resolve()/'vault')
    metadata, body, _ = split_note(path.read_text(encoding='utf-8'))
    require(metadata['type'] == 'Domain Term', 'Expected type: Domain Term')
    data = load(path)
    require(data.get('id') == identifier, 'Term ID must match filename')
    require(body.count(START) == 1 and body.count(END) == 1 and body.index(START) < body.index(END),
            'Expected exactly one term-definition block')
    definition = body.split(START, 1)[1].split(END, 1)[0].strip()
    context_id = data.get('context_id')
    ctx = contexts(root)
    require(context_id is None or context_id in ctx, f'{identifier}: unknown context')
    assets = definition_assets(root, path, definition)
    # Approval covers business content and unknown extension fields, not workflow or implementation mappings.
    excluded = {'status', 'observed_labels', 'questions', 'system_mappings', 'confirmation', 'confirmation_history'}
    semantic = {key: value for key, value in data.items() if key not in excluded}
    definition_revision = revision({'data': semantic, 'definition': definition,
                                    'context': ctx.get(context_id), 'assets': assets})
    source_revision = revision({'sha256': digest(path), 'context': ctx.get(context_id), 'assets': assets})
    return {'path': path, 'data': data, 'definition': definition, 'assets': assets,
            'definition_revision': definition_revision, 'source_revision': source_revision}


def label_keys(data):
    labels = [(language, name) for language, name in data['names'].items() if name]
    labels += [(alias['language'], alias['value']) for alias in data['aliases']]
    return {(language.casefold(), unicodedata.normalize('NFKC', name).strip().casefold())
            for language, name in labels}


def check_label_conflicts(root, data):
    labels = label_keys(data)
    for path in glossary_dir(root).glob('TERM-*.md'):
        if path.stem == data['id']:
            continue
        other = load(term_path(root, path.stem))
        if other.get('status') == 'confirmed' and other.get('context_id') == data['context_id']:
            require(not (labels & label_keys(other)), f'Ambiguous confirmed label in the same context: {other["id"]}')


def term_errors(root, term, confirming=False):
    data = term['data']; identifier = data['id']
    try:
        require(data['status'] in {'needs-clarification', 'proposed', 'confirmed', 'deprecated'}, 'Invalid term status')
        require(isinstance(data['observed_labels'], list) and all(text(v) for v in data['observed_labels']),
                'observed_labels must be a list of original words')
        require(isinstance(data['names'], dict) and all(text(k) and (v is None or text(v)) for k, v in data['names'].items()),
                'names must map language codes to text or null')
        require(isinstance(data['aliases'], list), 'aliases must be a list')
        for alias in data['aliases']:
            require(text(alias.get('language')) and text(alias.get('value')), 'Alias needs language and value')
        require(isinstance(data['sources'], list), 'sources must be a list')
        for source in data['sources']:
            require(text(source.get('path')) and text(source.get('revision')) and text(source.get('quote')),
                    'Term source needs path, revision and verbatim quote')
        require(isinstance(data['related_terms'], list) and len(data['related_terms']) == len(set(data['related_terms'])),
                'related_terms must contain unique IDs')
        for related in data['related_terms']:
            require(related != identifier and term_path(root, related).is_file(), 'Unknown/self related term')
        questions = records(data['questions'], 'term questions')
        for question in questions.values():
            require(text(question.get('question')) and re.fullmatch(r'TQ-[A-Za-z0-9-]+', question['id']),
                    'Term question needs TQ ID and question text')
            require(type(question['affects_definition']) is bool and question['status'] in {'open', 'resolved'},
                    'Invalid term question status or affects_definition')
            require(question.get('owner') is None or text(question['owner']), 'Question owner must be text or null')
            if question['status'] == 'resolved':
                require(all(text(question.get(k)) for k in ('answer', 'source', 'answered_by')),
                        'Resolved term question needs human answer, source and answered_by')
                timestamp(question.get('answered_at'))
        if data['status'] == 'proposed':
            require(text(term['definition']) and data['sources'], 'Proposed definition needs content and quoted source')
        if data['status'] == 'needs-clarification' and not confirming:
            require(any(q['status'] == 'open' for q in questions.values()), 'Unclear term needs an open question')
        if confirming or data['status'] == 'confirmed':
            require(text(visible_markdown(term['definition'])) and any(text(v) for v in data['names'].values()) and data['context_id'],
                    'Confirmation needs definition, preferred name and context')
            require(not any(q['affects_definition'] and q['status'] == 'open' for q in questions.values()),
                    'Open definition questions prevent confirmation')
            check_label_conflicts(root, data)
        if data['status'] == 'confirmed' and not confirming:
            approval = data.get('confirmation') or {}
            require(all(text(approval.get(k)) for k in ('by', 'source', 'revision')), 'Confirmation needs human by/source/revision')
            timestamp(approval.get('at'))
            require(approval['revision'] == term['definition_revision'], 'Confirmed definition changed; human reconfirmation required')
        for mapping in records(data['system_mappings'], 'system mappings').values():
            require(mapping['kind'] in {'current', 'proposed'}, 'System mapping kind must be current or proposed')
            require(all(text(mapping.get(k)) for k in ('path', 'revision', 'description')), 'System mapping needs path/revision/description')
            if mapping['kind'] == 'current':
                require(all(text(mapping.get(k)) for k in ('evidence', 'verified_by')), 'Current mapping needs verification evidence')
                timestamp(mapping.get('verified_at'))
            else:
                require(text(mapping.get('decision_ref')), 'Proposed mapping needs decision_ref (not approval)')
        require(isinstance(data['confirmation_history'], list), 'confirmation_history must be a list')
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        return [f'{identifier}: {exc}']
    return []


def validate_catalog(root):
    errors = []
    try:
        contexts(root)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        errors.append(f'Glossary contexts: {exc}')
    for path in sorted(glossary_dir(root).glob('TERM-*.md')):
        try:
            errors.extend(term_errors(root, read_term(root, path.stem)))
        except (OSError, KeyError, TypeError, ValueError) as exc:
            errors.append(f'{path.stem}: {exc}')
    return errors


def reviewed(record):
    require(record.get('status') == 'reviewed', 'Terminology review is pending')
    require(all(text(record.get(k)) for k in ('by', 'notes')), 'Terminology review needs by/notes')
    timestamp(record.get('at'))


def validate_references(root, req, ready=False):
    """Check only terms used by this assessment; unrelated pending terms do not block it."""
    errors = []
    try:
        refs = req.get('term_refs', [])
        require(isinstance(refs, list), 'term_refs must be a list')
        ids = [ref['term_id'] for ref in refs]
        require(len(ids) == len(set(ids)), 'Duplicate term reference')
        questions = records(req['questions'], 'questions')
        fr = records(req['functional_requirements'], 'functional_requirements')
        docs = records(req.get('source_documents', []), 'source_documents')
        shared = {}
        for ref in refs:
            term = read_term(root, ref['term_id']); data = term['data']
            errors.extend(term_errors(root, term))
            require(ref.get('source_revision') == term['source_revision'] and
                    ref.get('definition_revision') == term['definition_revision'],
                    f'{data["id"]}: stale term reference; refresh and reassess')
            require(ref.get('context_id') == data['context_id'], f'{data["id"]}: term context mismatch')
            require(ref['usage'] in {'meaning', 'background'}, 'Term usage must be meaning or background')
            require(isinstance(ref['functional_requirement_ids'], list) and set(ref['functional_requirement_ids']) <= fr.keys(),
                    'Unknown term FR reference')
            if ref['usage'] == 'background':
                require(not ref['functional_requirement_ids'] and text(ref.get('non_blocking_reason')),
                        'Background term needs non_blocking_reason and cannot define an FR')
            require(isinstance(ref['source_refs'], list), 'Term source_refs must be a list')
            for source in ref['source_refs']:
                doc = docs.get(source['document_id'])
                require(doc and source['item_id'] in doc['item_ids'], 'Unknown term BRD item reference')
            shared[data['id']] = records(data['questions'], 'term questions')
            linked = {q['term_question']['question_id'] for q in questions.values()
                      if q.get('term_question', {}).get('term_id') == data['id']}
            require({q['id'] for q in shared[data['id']].values() if q['status'] == 'open'} <= linked,
                    f'{data["id"]}: open term questions must be linked from the requirement')
            if ready:
                reviewed(ref.get('review', {}))
                if ref['usage'] == 'meaning':
                    require(data['status'] == 'confirmed', f'{data["id"]}: unconfirmed meaning blocks readiness')
        for q in questions.values():
            link = q.get('term_question')
            if not link:
                continue
            source = shared.get(link['term_id'], {}).get(link['question_id'])
            require(source is not None, f'{q["id"]}: dangling term question reference')
            ref = next(r for r in refs if r['term_id'] == link['term_id'])
            if source['affects_definition'] and ref['usage'] == 'meaning':
                require(q['blocking'] is True, f'{q["id"]}: definition uncertainty cannot be non-blocking')
            if q['status'] == 'resolved':
                require(source['status'] == 'resolved', f'{q["id"]}: shared question still open')
                require(q.get('term_revision') == ref['source_revision'], f'{q["id"]}: question impact review is stale')
        if ready:
            reviewed(req.get('terminology_review', {}))
    except (OSError, KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append(f'Terminology: {exc}')
    return errors


def input_paths(root, req):
    """Include referenced term files, contexts and definition assets in schedule provenance."""
    paths = {}
    for ref in req.get('term_refs', []):
        term = read_term(root, ref['term_id'])
        paths['term:' + ref['term_id']] = term['path']
        paths['term_contexts'] = glossary_dir(root)/'contexts.md'
        for asset in term['assets']:
            paths['term_asset:' + asset['path']] = Path(root)/asset['path']
    return paths
