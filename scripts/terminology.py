"""Create vocabulary stubs, record explicit human confirmation, link and review source changes."""
import argparse
from copy import deepcopy
from pathlib import Path

from common import ROOT, load, write, requirement_dir
from glossary import (contexts, glossary_dir, read_term, records, require,
                      term_errors, term_path, text, timestamp)
from okf import render_note, split_note


def pending_review():
    return {'status': 'pending', 'by': None, 'at': None, 'notes': None}


def create_term(root, identifier, label, context_id=None):
    path = term_path(root, identifier)
    require(not path.exists(), f'Refusing to overwrite {identifier}')
    require(text(label), 'Original label must not be blank')
    require(context_id is None or context_id in contexts(root), 'Unknown context')
    template = Path(root)/'vault/templates/term.md'
    metadata, body, _ = split_note(template.read_text(encoding='utf-8'))
    data = load(template)
    data.update(id=identifier, observed_labels=[label], context_id=context_id)
    metadata['title'] = f'{identifier} — {label}'
    from okf import block_span, data_block
    begin, end, _ = block_span(body)
    body = body[:begin] + data_block(data) + body[end:]
    body = body.replace('../docs/domain-terminology.md', '../../docs/domain-terminology.md')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_note(metadata, body), encoding='utf-8')
    return path


def confirm(root, identifier, expected_revision, by, at, source):
    term = read_term(root, identifier)
    require(term['definition_revision'] == expected_revision, 'Definition changed since human review')
    require(term['data']['status'] != 'deprecated', 'Cannot confirm a deprecated term')
    require(text(by) and text(source), 'Explicit human confirmation needs by and source')
    timestamp(at)
    errors = term_errors(root, term, confirming=True)
    require(not errors, '\n'.join(errors))
    data = term['data']
    if data.get('confirmation'):
        data['confirmation_history'].append(deepcopy(data['confirmation']))
    data.update(status='confirmed', confirmation={'by': by, 'at': at, 'source': source,
                                                 'revision': expected_revision})
    write(term['path'], data)


def draft_requirement(root, identifier):
    directory = requirement_dir(Path(root).resolve(), identifier)
    require(directory.resolve() == directory, 'Requirement path must not traverse symlinks')
    req, assessment = load(directory/'requirement.md'), load(directory/'assessment.md')
    require(req['status'] not in {'baseline', 'closed'} and assessment['status'] != 'baseline',
            'Cannot change baseline/closed requirements; create an authorized change assessment')
    return directory, req, assessment


def synchronize_questions(req, ref, term, reopen=False):
    existing = records(req['questions'], 'questions')
    for question in term['data']['questions']:
        link = {'term_id': ref['term_id'], 'question_id': question['id']}
        local = next((q for q in existing.values() if q.get('term_question') == link), None)
        if local is None and question['status'] == 'open':
            identifier = f'Q-{ref["term_id"]}-{question["id"]}'
            require(identifier not in existing, 'Question ID collision; resolve it before linking')
            local = {'id': identifier, 'question': f'Review {ref["term_id"]}/{question["id"]} and its impact on this requirement.',
                     'term_question': link, 'status': 'open', 'owner': question.get('owner') or 'requester'}
            req['questions'].append(local)
            existing[identifier] = local
        if local is not None:
            local['blocking'] = (ref['usage'] == 'meaning' and question['affects_definition']) or local.get('blocking', False)
            if reopen or question['status'] == 'open':
                local.update(status='open', term_revision=None)


def invalidate(directory, req, assessment, changed):
    req.update(status='intake', terminology_review=pending_review())
    assessment.update(ready_for_planning=False, reviewed_by=None, reviewed_at=None, owner_confirmation=None)
    assessment.setdefault('blockers', []).append('Terminology changed; reassess meanings and questions: ' + ', '.join(changed))
    write(directory/'requirement.md', req)
    write(directory/'assessment.md', assessment)


def link(root, requirement_id, term_id, fr_ids=None, sources=None, usage='meaning', reason=None):
    directory, req, assessment = draft_requirement(root, requirement_id)
    term = read_term(root, term_id)
    errors = term_errors(root, term)
    require(not errors, '\n'.join(errors))
    refs = req.setdefault('term_refs', [])
    require(not any(r['term_id'] == term_id for r in refs), 'Term already linked; use refresh or edit the reference')
    fr_ids, sources = fr_ids or [], sources or []
    require(len(fr_ids) == len(set(fr_ids)) and set(fr_ids) <= records(req['functional_requirements'], 'FRs').keys(),
            'Unknown or duplicate FR ID')
    require(usage in {'meaning', 'background'}, 'Invalid usage')
    require(usage != 'background' or (text(reason) and not fr_ids), 'Background needs reason and no FRs')
    docs = records(req.get('source_documents', []), 'source_documents')
    for src in sources:
        require(src['document_id'] in docs and src['item_id'] in docs[src['document_id']]['item_ids'], 'Unknown BRD item')
    ref = {'term_id': term_id, 'context_id': term['data']['context_id'], 'usage': usage,
           'non_blocking_reason': reason, 'functional_requirement_ids': fr_ids, 'source_refs': sources,
           'definition_revision': term['definition_revision'], 'source_revision': term['source_revision'],
           'review': pending_review()}
    refs.append(ref)
    synchronize_questions(req, ref, term)
    invalidate(directory, req, assessment, [term_id])


def refresh(root, requirement_id):
    directory, req, assessment = draft_requirement(root, requirement_id)
    changed = []
    for ref in req.get('term_refs', []):
        term = read_term(root, ref['term_id'])
        if ref.get('source_revision') == term['source_revision']:
            continue
        changed.append(ref['term_id'])
        ref.update(source_revision=term['source_revision'], definition_revision=term['definition_revision'],
                   context_id=term['data']['context_id'], review=pending_review())
        synchronize_questions(req, ref, term, reopen=True)
    # Removed questions and invalid FR/BRD references are retained for explicit reconciliation.
    if changed:
        invalidate(directory, req, assessment, changed)
    return changed


def cell(value):
    return str(value if value is not None else '待指定').replace('|', '\\|').replace('\n', ' ').replace('[', '').replace(']', '')


def report(root):
    directory = glossary_dir(root)
    intro = ('[上下文](contexts.md) · [待釐清與影響清單](clarification-queue.md) · '
             '[操作規約](../../docs/domain-terminology.md)')
    navigation = ['# 領域詞彙庫', '', '由 `python scripts/terminology.py report` 更新；正式內容請編輯各術語頁。', '', intro, '',
                  '| 術語 | 原始用語 | 正式名稱及別名 | 上下文 | 狀態 |', '|---|---|---|---|---|']
    queue = ['# 術語待釐清與影響清單', '', '此頁為衍生檢視；回答在術語頁維護，需求影響在需求頁檢閱。', '',
             '| 術語／問題 | 內容 | 負責人 |', '|---|---|---|']
    terms = {}
    for path in sorted(directory.glob('TERM-*.md')):
        term = read_term(root, path.stem); terms[path.stem] = term
        data = term['data']
        names = [f'{k}: {v}' for k, v in data['names'].items() if v]
        names += [f'{a["language"]}: {a["value"]}' for a in data['aliases']]
        navigation.append(f'| [{data["id"]}]({path.name}) | {cell(", ".join(data["observed_labels"]))} | '
                          f'{cell("; ".join(names))} | {cell(data["context_id"])} | {data["status"]} |')
        for question in data['questions']:
            if question['status'] == 'open':
                queue.append(f'| [{data["id"]}/{question["id"]}]({path.name}) | {cell(question["question"])} | {cell(question.get("owner"))} |')
        for error in term_errors(root, term):
            queue.append(f'| [{data["id"]}]({path.name}) | {cell(error)} | 待檢閱 |')
    queue += ['', '## 需求影響', '', '| 需求 | 術語 | 需處理事項 |', '|---|---|---|']
    for req_path in sorted((Path(root)/'vault/requirements').glob('REQ-*/requirement.md')):
        req = load(req_path)
        for ref in req.get('term_refs', []):
            term = terms.get(ref['term_id']); issues = []
            if term is None:
                issues.append('術語遺失')
            else:
                if ref.get('source_revision') != term['source_revision']:
                    issues.append('引用版本已變更，需重新擷取與檢閱')
                if ref['usage'] == 'meaning' and term['data']['status'] != 'confirmed':
                    issues.append('業務定義尚未確認或已停用')
                if term_errors(root, term):
                    issues.append('術語紀錄或確認版本需修正')
            if ref.get('review', {}).get('status') != 'reviewed':
                issues.append('需求影響尚未檢閱')
            if any(q.get('term_question', {}).get('term_id') == ref['term_id'] and q['status'] == 'open'
                   for q in req['questions']):
                issues.append('需求仍有待處理的術語問題')
            if issues:
                target = f'../../requirements/{req_path.parent.name}/requirement.md'
                queue.append(f'| [{req_path.parent.name}]({target}) | {ref["term_id"]} | {"；".join(issues)} |')
    if not terms:
        navigation += ['', '尚未登錄術語。']
        queue += ['', '尚未登錄術語。']
    queue += ['', '[詞彙首頁](index.md)']
    metadata, _, _ = split_note((directory/'clarification-queue.md').read_text(encoding='utf-8'))
    metadata.pop('verified', None)
    (directory/'index.md').write_text('\n'.join(navigation) + '\n', encoding='utf-8')
    (directory/'clarification-queue.md').write_text(render_note(metadata, '\n'.join(queue)), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('id'); init.add_argument('--label', required=True); init.add_argument('--context')
    rev = commands.add_parser('revision'); rev.add_argument('id')
    approval = commands.add_parser('confirm'); approval.add_argument('id')
    for arg in ('revision', 'by', 'at', 'source'):
        approval.add_argument('--' + arg, required=True)
    attach = commands.add_parser('link'); attach.add_argument('requirement'); attach.add_argument('id')
    attach.add_argument('--fr', action='append', default=[])
    attach.add_argument('--source-item', action='append', default=[], metavar='BRD-ID/br-ID')
    attach.add_argument('--usage', choices=['meaning', 'background'], default='meaning'); attach.add_argument('--reason')
    recapture = commands.add_parser('refresh'); recapture.add_argument('requirement')
    commands.add_parser('report')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            print(create_term(args.root, args.id, args.label, args.context)); report(args.root)
        elif args.command == 'revision':
            print(read_term(args.root, args.id)['definition_revision'])
        elif args.command == 'confirm':
            confirm(args.root, args.id, args.revision, args.by, args.at, args.source); report(args.root)
            print('Recorded supplied human confirmation; reassess affected requirements')
        elif args.command == 'link':
            sources = []
            for value in args.source_item:
                parts = value.split('/')
                require(len(parts) == 2, 'Expected BRD-ID/br-ID')
                sources.append({'document_id': parts[0], 'item_id': parts[1]})
            link(args.root, args.requirement, args.id, args.fr, sources, args.usage, args.reason); report(args.root)
            print('Linked term; meaning, questions and requirement impact still need review')
        elif args.command == 'refresh':
            changed = refresh(args.root, args.requirement); report(args.root)
            print('Refreshed: ' + ', '.join(changed) if changed else 'Term inputs unchanged')
        else:
            report(args.root); print('Updated vocabulary index and clarification/impact report')
    except (OSError, KeyError, TypeError, ValueError, AttributeError) as exc:
        raise SystemExit(str(exc))


if __name__ == '__main__':
    main()
