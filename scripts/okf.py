"""OKF Markdown I/O and the project-agent/v1 structured-data profile.

This is a local profile checker, not a complete OKF consumer or executor.
"""
from datetime import datetime
from pathlib import Path
import re
import yaml

PROFILE = 'project-agent/v1'
START = '<!-- project-data:start -->'
END = '<!-- project-data:end -->'


class UniqueLoader(yaml.SafeLoader):
    """Reject ambiguous duplicate keys in facts and frontmatter."""


def _mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            if key in result:
                raise ValueError(f'Duplicate YAML key: {key}')
            result[key] = loader.construct_object(value_node, deep=deep)
        except TypeError as exc:
            raise ValueError('YAML mapping keys must be scalar') from exc
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def parse_yaml(text):
    return yaml.load(text, Loader=UniqueLoader)


def dump_yaml(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def split_note(text):
    match = re.match(r'\A---\n(.*?)\n---(?:\n|\Z)', text, re.DOTALL)
    if not match:
        raise ValueError('Expected YAML frontmatter bounded by ---')
    metadata = parse_yaml(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError('Frontmatter must be a mapping')
    return metadata, text[match.end():], match.end()


def render_note(metadata, body):
    return '---\n' + dump_yaml(metadata) + '---\n\n' + body.strip() + '\n'


def block_span(body):
    if body.count(START) != 1 or body.count(END) != 1:
        raise ValueError('Expected exactly one marked project-data block')
    start = body.index(START)
    end = body.index(END, start) + len(END)
    interior = body[start + len(START):end - len(END)].strip()
    match = re.fullmatch(r'```yaml\n(.*?)\n```', interior, re.DOTALL)
    if not match:
        raise ValueError('project-data must contain exactly one fenced yaml block')
    return start, end, match.group(1)


def data_block(data):
    return START + '\n```yaml\n' + dump_yaml(data) + '```\n' + END


def load_data(path):
    text = Path(path).read_text(encoding='utf-8')
    metadata, body, _ = split_note(text)
    if metadata.get('project_profile') != PROFILE:
        raise ValueError(f'Expected project_profile: {PROFILE}')
    _, _, payload = block_span(body)
    data = parse_yaml(payload)
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Project data must be a mapping with schema_version: 1')
    return data


def write_data(path, data):
    """Replace only the data block; retain frontmatter, unknown keys and prose."""
    path = Path(path)
    if path.exists():
        text = path.read_text(encoding='utf-8')
        metadata, body, offset = split_note(text)
        if metadata.get('project_profile') != PROFILE:
            raise ValueError(f'Expected project_profile: {PROFILE}')
        start, end, _ = block_span(body)
        text = text[:offset] + body[:start] + data_block(data) + body[end:]
    else:
        metadata = {'type': 'Project Data', 'title': path.stem,
                    'status': 'draft', 'project_profile': PROFILE}
        text = render_note(metadata, f'# {path.stem}\n\n{data_block(data)}')
    path.write_text(text, encoding='utf-8')


def _timestamp(value):
    if not isinstance(value, (str, datetime)):
        raise ValueError('OKF timestamps need a datetime with an explicit UTC offset')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00')) if isinstance(value, str) else value
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('OKF timestamps need an explicit UTC offset')


def check_note(path, bundle):
    """Check supported OKF envelope fields; accept custom types/unknown fields."""
    path, bundle = Path(path), Path(bundle)
    text = path.read_text(encoding='utf-8')
    if path.name in {'index.md', 'log.md'}:
        if text.startswith('---\n'):
            metadata, _, _ = split_note(text)
            if path != bundle/'index.md' or set(metadata) != {'okf_version'} or metadata['okf_version'] != '0.2':
                raise ValueError('Only bundle-root index.md may have okf_version: "0.2" frontmatter')
        if path.name == 'log.md':
            for line in text.splitlines():
                if line.startswith('## '):
                    datetime.strptime(line[3:], '%Y-%m-%d')
        return
    metadata, _, _ = split_note(text)
    if not isinstance(metadata.get('type'), str) or not metadata['type'].strip():
        raise ValueError('OKF concept requires a nonempty type')
    if metadata.get('status', 'stable') not in {'draft', 'stable', 'deprecated'}:
        raise ValueError('OKF status must be draft, stable or deprecated; workflow status belongs in project-data')
    for key in ('title', 'description', 'resource'):
        if key in metadata and not isinstance(metadata[key], str):
            raise ValueError(f'{key} must be text')
    if 'sources' in metadata:
        sources = metadata['sources']
        if not isinstance(sources, list):
            raise ValueError('OKF sources must be a list')
        for source in sources:
            if not isinstance(source, dict) or not isinstance(source.get('resource'), str) or not source['resource'].strip():
                raise ValueError('Every OKF source needs resource; the repo registry lives in project-data')
            if 'last_modified' in source:
                _timestamp(source['last_modified'])
    if 'generated' in metadata:
        event = metadata['generated']
        if not isinstance(event, dict) or not isinstance(event.get('by'), str) or not event['by'].strip():
            raise ValueError('generated needs by')
        if 'at' in event:
            _timestamp(event['at'])
    if 'verified' in metadata:
        events = metadata['verified']
        events = [events] if isinstance(events, dict) else events
        if not isinstance(events, list) or not events:
            raise ValueError('verified must be an event or a nonempty event list')
        for event in events:
            if not isinstance(event, dict) or not isinstance(event.get('by'), str) or not event['by'].strip():
                raise ValueError('verified event needs by')
            _timestamp(event.get('at'))
    if 'stale_after' in metadata:
        _timestamp(metadata['stale_after'])
    if metadata.get('type') == 'Attested Computation' and not metadata.get('runtime'):
        raise ValueError('Attested Computation requires runtime')
    if metadata.get('project_profile') == PROFILE:
        load_data(path)


def write_directory_index(directory, title):
    """Refresh a generated local navigation page; never traverse baseline copies."""
    directory = Path(directory)
    lines = [f'# {title}', '', '此索引由工具維護；內容請編輯各連結頁面。', '']
    for child in sorted(directory.iterdir()):
        if child.name.startswith('.') or child.name in {'index.md', 'log.md'}:
            continue
        if child.is_dir() and (child/'index.md').exists():
            lines.append(f'- [{child.name}]({child.name}/index.md)')
        elif child.suffix == '.md':
            metadata, _, _ = split_note(child.read_text(encoding='utf-8'))
            title = str(metadata.get('title', child.stem)).replace('[', '').replace(']', '')
            description = metadata.get('description', '')
            lines.append(f'- [{title}]({child.name})' + (f' — {description}' if description else ''))
    (directory/'index.md').write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
