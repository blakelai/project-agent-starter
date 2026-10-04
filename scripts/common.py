"""Deterministic helpers; no network, LLM or OpenWiki dependency."""
from pathlib import Path
from datetime import date, timedelta
import hashlib
import math
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with Path(path).open(encoding='utf-8') as stream:
        return yaml.safe_load(stream)

def write(path, data):
    Path(path).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')

def day(value):
    return value if isinstance(value, date) else date.fromisoformat(str(value))

def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def requirement_dir(root, identifier):
    import re
    if not re.fullmatch(r'REQ-[A-Za-z0-9][A-Za-z0-9-]{0,63}', identifier):
        raise ValueError('Requirement ID must match REQ-<letters/digits/hyphens>')
    return Path(root) / 'requirements' / identifier

def index(items, label):
    result = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            raise ValueError(f'{label}: every item needs a string id')
        if item['id'] in result:
            raise ValueError(f'{label}: duplicate ID {item["id"]}')
        result[item['id']] = item
    return result

def topological(packages):
    by_id = index(packages, 'work_packages')
    order, visiting, visited = [], set(), set()
    def visit(identifier):
        if identifier in visiting:
            raise ValueError(f'Dependency cycle at {identifier}')
        if identifier in visited:
            return
        if identifier not in by_id:
            raise ValueError(f'Missing dependency {identifier}')
        visiting.add(identifier)
        deps = by_id[identifier].get('depends_on', [])
        if not isinstance(deps, list) or len(deps) != len(set(deps)):
            raise ValueError(f'{identifier}: invalid dependencies')
        for dependency in deps:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)
        order.append(identifier)
    for identifier in by_id:
        visit(identifier)
    return order

def fraction_on(current, person, capacity, calendar):
    if current < day(capacity['valid_from']) or current > day(capacity['valid_until']):
        raise ValueError('Schedule exceeds capacity validity window')
    record = capacity['people'][person]
    if current.weekday() not in calendar['work_weekdays']:
        return 0.0
    if current in {day(x) for x in calendar.get('holidays', [])}:
        return 0.0
    if current in {day(x) for x in record.get('leave', [])}:
        return 0.0
    return float(record['fraction'])

def allocate(earliest, person, effort, capacity, calendar):
    remaining, current, entries = float(effort), earliest, []
    while remaining > 1e-9:
        fraction = fraction_on(current, person, capacity, calendar)
        if fraction > 0:
            consumed = min(fraction, remaining)
            entries.append({'date':current.isoformat(), 'effort_pd':round(consumed, 6)})
            remaining -= consumed
        current += timedelta(days=1)
    return entries

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
