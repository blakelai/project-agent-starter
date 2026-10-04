"""Greedy feasible full-day schedule, not optimal RCPSP or a calibrated percentile forecast."""
import argparse
from pathlib import Path
from datetime import timedelta
from common import ROOT, load, write, day, index, topological, allocate, digest, requirement_dir
from validate import validate

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
    paths={'work_breakdown':directory/'work-breakdown.yaml','estimation':directory/'estimation.yaml',
           'capacity':args.root/'planning/capacity.yaml','calendar':args.root/'planning/calendar.yaml',
           'requirement':directory/'requirement.yaml','assessment':directory/'assessment.yaml',
           'people':args.root/'planning/people.yaml','risks':directory/'risks.yaml'}
    calendar=load(paths['calendar']); start=day(args.start or calendar['start_date'])
    try:
        result=compute(load(paths['work_breakdown'])['work_packages'],load(paths['estimation'])['estimates'],
                       load(paths['capacity']),calendar,args.scenario,start)
    except ValueError as exc: raise SystemExit(str(exc))
    result['input_sha256']={key:digest(path) for key,path in paths.items()}
    target=directory/f'schedule-{args.scenario}.yaml'; write(target,result)
    print(f'{args.scenario}: {result["total_effort_pd"]} PD; {start} through {result["finish_date"]}; wrote {target.name}')
if __name__=='__main__': main()
