"""Greedy feasible full-day schedule, not optimal RCPSP or a calibrated percentile forecast."""
import argparse
from pathlib import Path
from datetime import timedelta, datetime, timezone
from common import ROOT, load, day, index, topological, allocate, digest, requirement_dir
from validate import validate
from glossary import input_paths as terminology_inputs
from okf import PROFILE, render_note, data_block, split_note, write_directory_index

def save_report(target, result):
    metadata = split_note(target.read_text(encoding='utf-8'))[0] if target.exists() else {}
    metadata.pop('verified', None)  # A recomputation is not a renewed human verification.
    metadata.update(type='Project Schedule', title=f'{result["scenario"]} 排程',
                    description='由專案資料重算的排程情境與輸入雜湊。', status='draft',
                    project_profile=PROFILE,
                    generated={'by':'project-agent-scheduler/v1', 'at':datetime.now(timezone.utc).isoformat()})
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = [f'# {result["scenario"]} 排程', '',
             '本頁由排程工具產生，重算時更新本文。修改需求、WBS、估算或規劃輸入後再重算。', '',
             f'期間：{result["start_date"]} 至 {result["finish_date"]}；總工時：{result["total_effort_pd"]} PD。', '',
             '| 工作包 | 負責人 | 開始 | 完成 | PD | 使用工作日 |',
             '|---|---|---|---|---|---|']
    for task in result['tasks']:
        lines.append('| ' + ' | '.join(cell(task[k]) for k in ['id','assigned_to','start','finish','effort_pd','workdays_used']) + ' |')
    lines += ['', '情境結果不代表交付百分位；此工具使用單一負責人、整日保留的 greedy 排程模型。', '',
              '## 關聯', '', '[工作分解](work-breakdown.md) · [工時估算](estimation.md) · '
              '[容量](../../planning/capacity.md) · [日曆](../../planning/calendar.md) · [需求導覽](index.md)', '',
              '## 計算結果與輸入雜湊', '', data_block(result)]
    target.write_text(render_note(metadata, '\n'.join(lines)), encoding='utf-8')

def compute(packages, estimates, capacity, calendar, scenario, start):
    by_id=index(packages,'work packages'); est=index(estimates,'estimates')
    order=topological(packages)
    if not order: raise ValueError('Cannot schedule empty WBS')
    # Lower bound ignores competing use of the same resource but respects individual calendars.
    lower, chains={},{}
    for identifier in order:
        p=by_id[identifier]; deps=p['depends_on']
        terminal=max(deps,key=lambda d:lower[d],default=None)
        earliest=max(start,day(p['not_before']) if p.get('not_before') else start,
                     lower[terminal]+timedelta(days=1) if terminal else start)
        entries=allocate(earliest,p['assigned_to'],est[identifier]['effort_pd'][scenario],capacity,calendar)
        lower[identifier]=day(entries[-1]['date'])
        chains[identifier]=(chains[terminal] if terminal else [])+[identifier]
    finished={}; free={person:start for person in capacity['people']}; rows=[]
    while len(finished)<len(by_id):
        ready=[p for p in packages if p['id'] not in finished and set(p['depends_on'])<=finished.keys()]
        if not ready: raise ValueError('Dependency graph has no schedulable work')
        candidates=[]
        for p in ready:
            earliest=max(start,free[p['assigned_to']],day(p['not_before']) if p.get('not_before') else start,
                         max((finished[d]+timedelta(days=1) for d in p['depends_on']),default=start))
            entries=allocate(earliest,p['assigned_to'],est[p['id']]['effort_pd'][scenario],capacity,calendar)
            candidates.append((day(entries[0]['date']),p['priority'],p['id'],entries))
        _,_,identifier,entries=min(candidates,key=lambda c:c[:3]); p=by_id[identifier]
        end=day(entries[-1]['date']); finished[identifier]=end; free[p['assigned_to']]=end+timedelta(days=1)
        rows.append({'id':identifier,'assigned_to':p['assigned_to'],'start':entries[0]['date'],
                     'finish':entries[-1]['date'],'effort_pd':est[identifier]['effort_pd'][scenario],
                     'workdays_used':len(entries),'allocations':entries})
    terminal=max(lower,key=lambda d:lower[d]); finish=max(finished.values())
    return {'schema_version':1,'scenario':scenario,'method':'greedy-full-day-single-assignee-v1',
            'is_project_percentile':False,'start_date':start.isoformat(),'finish_date':finish.isoformat(),
            'total_effort_pd':round(sum(e['effort_pd'][scenario] for e in estimates),6),
            'calendar_days_inclusive':(finish-start).days+1,
            'precedence_only_lower_bound_end':lower[terminal].isoformat(),
            'precedence_only_terminal_chain':chains[terminal],
            'resource_delay_calendar_days':(finish-lower[terminal]).days,
            'tasks':sorted(rows,key=lambda r:(r['start'],r['id']))}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT); parser.add_argument('--requirement',required=True)
    parser.add_argument('--scenario',choices=['low','expected','high'],default='expected')
    parser.add_argument('--start'); args=parser.parse_args()
    directory=requirement_dir(args.root,args.requirement)
    errors=validate(args.root,directory,planning=True)
    if errors: raise SystemExit('\n'.join(errors))
    paths={'work_breakdown':directory/'work-breakdown.md','estimation':directory/'estimation.md',
           'capacity':args.root/'vault/planning/capacity.md','calendar':args.root/'vault/planning/calendar.md',
           'requirement':directory/'requirement.md','assessment':directory/'assessment.md',
           'people':args.root/'vault/planning/people.md','risks':directory/'risks.md',
           'evidence':directory/'evidence.md','traceability':directory/'traceability.md',
           'sources':args.root/'vault/knowledge/sources.md','project':args.root/'vault/config/project.md',
           'historical_delivery':args.root/'vault/planning/historical-delivery.md',
           'estimation_rules':args.root/'vault/planning/estimation-rules.md',
           'work_types':args.root/'vault/planning/work-types.md'}
    for doc in load(paths['requirement']).get('source_documents', []):
        paths['brd:'+doc['id']]=args.root/doc['path']
        for asset in doc['assets']:
            paths['asset:'+asset['path']]=args.root/asset['path']
    paths.update(terminology_inputs(args.root, load(paths['requirement'])))
    calendar=load(paths['calendar']); start=day(args.start or calendar['start_date'])
    try:
        result=compute(load(paths['work_breakdown'])['work_packages'],load(paths['estimation'])['estimates'],
                       load(paths['capacity']),calendar,args.scenario,start)
    except ValueError as exc: raise SystemExit(str(exc))
    result['input_sha256']={key:digest(path) for key,path in paths.items()}
    target=directory/f'schedule-{args.scenario}.md'; save_report(target,result)
    write_directory_index(directory, args.requirement)
    print(f'{args.scenario}: {result["total_effort_pd"]} PD; {start} through {result["finish_date"]}; wrote {target.name}')
if __name__=='__main__': main()
