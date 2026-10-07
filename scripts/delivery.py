"""Delivery observations and human acceptance checks; never infer completion or remaining effort."""
from common import day, index, number
from glossary import require, text, timestamp


def approval(record, reason=False):
    require(isinstance(record, dict) and all(text(record.get(k)) for k in ['by', 'source']),
            'Human decision needs by, at and source')
    timestamp(record.get('at'))
    if reason:
        require(text(record.get('reason')), 'Exception/cancellation needs a reason')


def progress_errors(progress, packages, links, closing=False, forecasting=False):
    try:
        require(progress.get('as_of'), 'Progress needs as_of')
        as_of = day(progress['as_of'])
        work = index(progress['work'], 'progress work')
        require(set(work) == set(packages), 'Progress must cover exactly the current WP IDs')
        for identifier, row in work.items():
            require(row['status'] in {'not-started', 'in-progress', 'blocked', 'done', 'cancelled'},
                    f'{identifier}: invalid work status')
            actual = row.get('actual_effort_pd')
            require(actual is None or (number(actual) and actual >= 0), f'{identifier}: invalid actual effort')
            if actual is None:
                require(text(row.get('actual_unknown_reason')), f'{identifier}: explain unknown actual effort')
            remaining = row.get('remaining_effort_pd')
            if remaining is not None:
                require(isinstance(remaining, dict) and all(number(remaining.get(k)) and remaining[k] >= 0
                        for k in ['low', 'expected', 'high']), f'{identifier}: invalid remaining effort')
                require(remaining['low'] <= remaining['expected'] <= remaining['high'], f'{identifier}: unordered remaining effort')
            if row['status'] in {'done', 'cancelled'}:
                require(remaining is not None and all(remaining[k] == 0 for k in ['low', 'expected', 'high']),
                        f'{identifier}: completed/cancelled work needs zero remaining effort')
                if row['status'] == 'done':
                    require(text(row.get('completion_evidence')) and row.get('completed_on'), f'{identifier}: completion needs evidence/date')
                    require(day(row['completed_on']) <= as_of, f'{identifier}: completion after as_of')
                else:
                    approval(row.get('cancellation'), reason=True)
            elif forecasting:
                require(remaining is not None and all(remaining[k] > 0 for k in ['low', 'expected', 'high']),
                        f'{identifier}: forecast requires positive, explicitly estimated remaining effort')
                if row['status'] == 'blocked':
                    require(row.get('resume_on') and text(row.get('resume_source')), f'{identifier}: unknown unblock date prevents forecast')
                    require(day(row['resume_on']) > as_of, f'{identifier}: unblock date must follow as_of')
            if closing:
                require(row['status'] in {'done', 'cancelled'}, f'{identifier}: unfinished work prevents closure')
        for blocker in index(progress.get('blockers', []), 'progress blockers').values():
            require(text(blocker.get('description')) and text(blocker.get('owner')), 'Progress blocker needs description/owner')
            require(blocker['status'] in {'open', 'resolved'}, 'Invalid blocker status')
            require(set(blocker['work_packages']) <= packages.keys(), 'Unknown blocker work package')
            if forecasting and blocker['status'] == 'open':
                require(bool(blocker['work_packages']), 'Open forecast blocker needs affected work packages')
                require(all(work[wid]['status'] == 'blocked' for wid in blocker['work_packages']),
                        'Open forecast blocker must match blocked work status')
            if blocker['status'] == 'resolved':
                require(text(blocker.get('resolution')), 'Resolved blocker needs resolution')
            if closing:
                require(blocker['status'] == 'resolved', 'Open delivery blocker prevents closure')
        if closing:
            seen = set()
            for link in links:
                aid = link['acceptance_id']
                require(aid not in seen, 'Duplicate AC closure record')
                seen.add(aid)
                decision = link.get('acceptance') or {}
                require(decision.get('status') in {'accepted', 'waived'}, f'{aid}: human acceptance/waiver required')
                approval(decision, reason=decision['status'] == 'waived')
                if decision['status'] == 'accepted':
                    require(link['test_status'] == 'passed' and text(link.get('test_evidence')),
                            f'{aid}: accepted AC needs passed tests and evidence')
            approval(progress.get('closure'))
            require(text(progress['closure'].get('summary')), 'Closure needs a summary of scope/results/lessons')
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        return [f'Delivery: {exc}']
    return []
