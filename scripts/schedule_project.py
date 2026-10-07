"""Plan all selected REQs together, or forecast explicit remaining work after an as-of date."""
import argparse
from copy import deepcopy
from datetime import timedelta, datetime, timezone
from pathlib import Path

from common import ROOT, load, day, index, digest
from delivery import progress_errors
from glossary import require
from okf import PROFILE, render_note, split_note, data_block, write_directory_index
from project import collect, project_dir
from schedule import compute


def remaining_inputs(root, packages, estimates, progress, as_of):
    remaining, finished, cancelled, observations = [], [], set(), {}
    for req_id, data in progress.items():
        require(day(data['as_of'])==as_of, f'{req_id}: progress as_of must match the forecast cutoff')
        local={p['work_package_id']:p for p in packages if p['requirement_id']==req_id}
        local_links=load(Path(root)/'vault/requirements'/req_id/'traceability.md')['links']
        errors=progress_errors(data,local,local_links,forecasting=True)
        require(not errors,req_id+': '+'; '.join(errors))
        for row in data['work']: observations[req_id+'/'+row['id']]=deepcopy(row)
    for wp in packages:
        row=observations[wp['id']]
        if row['status']=='done':
            finished.append(wp['id'])
        elif row['status']=='cancelled':
            cancelled.add(wp['id'])
        else:
            item=deepcopy(wp)
            require(not(set(item['depends_on'])&cancelled), 'Cancelled predecessor requires an explicit dependency change')
            if row['status']=='blocked':
                item['not_before']=max(day(item['not_before']) if item.get('not_before') else as_of,day(row['resume_on'])).isoformat()
            remaining.append(item)
    # Inspect after the complete cancellation set is known, regardless of original package order.
    for item in remaining:
        require(not(set(item['depends_on'])&cancelled), 'Cancelled predecessor requires an explicit dependency change')
        item['depends_on']=[dep for dep in item['depends_on'] if dep not in finished]
    estimate_by_id=index(estimates,'estimates')
    for wp in remaining:
        estimate_by_id[wp['id']]['effort_pd']=observations[wp['id']]['remaining_effort_pd']
    return remaining,[estimate_by_id[p['id']] for p in remaining],observations


def build(root, identifier, scenario='expected', as_of=None, start=None):
    forecast=as_of is not None
    manifest, packages, estimates, progress, inputs=collect(root,identifier,forecast)
    calendar=load(Path(root)/'vault/planning/calendar.md')
    capacity=load(Path(root)/'vault/planning/capacity.md')
    observations={}
    if forecast:
        cutoff=day(as_of); start_date=cutoff+timedelta(days=1)
        require(start is None,'Forecast starts after as_of; do not supply --start')
        packages, estimates, observations=remaining_inputs(root,packages,estimates,progress,cutoff)
    else:
        start_date=day(start or calendar['start_date'])
    if packages:
        result=compute(packages,estimates,capacity,calendar,scenario,start_date)
    else:
        require(forecast,'Cannot schedule empty project scope')
        result={'schema_version':1,'scenario':scenario,'method':'greedy-full-day-single-assignee-v1',
                'is_project_percentile':False,'start_date':day(as_of).isoformat(),'finish_date':day(as_of).isoformat(),
                'total_effort_pd':0,'tasks':[],'no_remaining_work':True}
    result.update(project_id=identifier,mode='remaining-work' if forecast else 'full-work',
                  selected_requirements=[r['id'] for r in manifest['requirements']],
                  input_sha256={str(path.relative_to(Path(root).resolve())):digest(path) for path in inputs.values()})
    if forecast:
        result.update(as_of=day(as_of).isoformat(),observed_work=observations,
                      actual_effort_known_pd=sum(r['actual_effort_pd'] for r in observations.values() if r.get('actual_effort_pd') is not None),
                      actual_effort_unknown=[key for key,row in observations.items() if row.get('actual_effort_pd') is None])
    return result


def save(target, result):
    metadata=split_note(target.read_text(encoding='utf-8'))[0] if target.exists() else {}
    metadata.pop('verified',None)
    metadata.update(type='Project Schedule',title=f'{result["project_id"]} — {result["mode"]} {result["scenario"]}',
                    status='draft',project_profile=PROFILE,
                    generated={'by':'project-agent-project-scheduler/v1','at':datetime.now(timezone.utc).isoformat()})
    lines=[f'# {metadata["title"]}','','所有選定需求共用同一份人員容量。此為確定性情境，不是交付百分位。','',
           f'期間：{result["start_date"]} 至 {result["finish_date"]}；本次排程工作量：{result["total_effort_pd"]} PD。','',
           '| 需求／工作包 | 負責人 | 開始 | 完成 | PD |','|---|---|---|---|---|']
    for task in result['tasks']:
        req_id,wp_id=task['id'].split('/',1)
        lines.append(f'| [{req_id}/{wp_id}](../../requirements/{req_id}/work-breakdown.md) | {task["assigned_to"]} | {task["start"]} | {task["finish"]} | {task["effort_pd"]} |')
    if result['mode']=='remaining-work':
        lines += ['',f'觀測截止日：{result["as_of"]}（含當日）。實際已完成工作保持原紀錄；排程從次日開始。',
                  f'已知實際投入：{result["actual_effort_known_pd"]} PD；未知實際投入工作包：{len(result["actual_effort_unknown"])}。']
    lines += ['',data_block(result),'','[專案範圍](project.md) · [工作流程](../../docs/project-workflow.md) · [回到目錄](index.md)']
    target.write_text(render_note(metadata,'\n'.join(lines)),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT); parser.add_argument('--project',required=True)
    parser.add_argument('--scenario',choices=['low','expected','high'],default='expected')
    parser.add_argument('--start'); parser.add_argument('--as-of',help='Forecast remaining work after this inclusive observation date')
    args=parser.parse_args()
    try:
        result=build(args.root,args.project,args.scenario,args.as_of,args.start)
        directory=project_dir(args.root,args.project)
        target=directory/(('forecast-' if args.as_of else 'schedule-')+args.scenario+'.md')
        save(target,result); write_directory_index(directory,args.project)
    except (OSError,KeyError,TypeError,ValueError,AttributeError) as exc:
        raise SystemExit(str(exc))
    print(f'Wrote {target}; finish {result["finish_date"]}; {result["total_effort_pd"]} PD')


if __name__=='__main__': main()
