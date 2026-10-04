"""Validate v1 artifacts and cross-file consistency. Does not validate truth or approval identity."""
import argparse
from pathlib import Path
from common import ROOT, load, day, number, requirement_dir, index, topological

ARTIFACTS = ['requirement.yaml','evidence.yaml','work-breakdown.yaml','estimation.yaml',
             'risks.yaml','traceability.yaml','assessment.yaml']

def validate(root, directory, planning=False):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    data = {}
    for filename in ARTIFACTS:
        try:
            data[filename] = load(directory/filename)
            require(isinstance(data[filename],dict), f'{filename}: expected mapping')
            require(data[filename].get('schema_version') == 1, f'{filename}: unsupported schema')
        except Exception as exc:
            errors.append(f'{filename}: {exc}')
    if errors:
        return errors
    try:
        req=data['requirement.yaml']; assess=data['assessment.yaml']
        require(req['id'] == directory.name,'Requirement ID must match directory')
        require(req['status'] in ['intake','clarified','assessed','baseline','closed'],'Invalid requirement status')
        for field in ['goal','actors','scope','non_goals','constraints','facts','questions','functional_requirements','acceptance_criteria']:
            require(field in req, f'Requirement missing {field}')
        sources=index(load(root/'knowledge/sources.yaml')['sources'],'sources')
        evidence=index(data['evidence.yaml']['evidence'],'evidence')
        ac=index(req['acceptance_criteria'],'acceptance criteria')
        fr=index(req['functional_requirements'],'functional requirements')
        questions=index(req['questions'],'questions')
        packages=data['work-breakdown.yaml']['work_packages']; wp=index(packages,'work packages')
        estimates=index(data['estimation.yaml']['estimates'],'estimates')
        risks=index(data['risks.yaml']['risks'],'risks')
        historical=index(load(root/'planning/historical-delivery.yaml')['samples'],'historical samples')
        types=load(root/'planning/work-types.yaml')['work_types']
        people_data=load(root/'planning/people.yaml')
        people=index(people_data['people'],'people')
        capacity=load(root/'planning/capacity.yaml'); calendar=load(root/'planning/calendar.yaml')
        if planning and not req.get('synthetic',False):
            project=load(root/'config/project.yaml')
            require(bool(project.get('owner')) and 'REPLACE_' not in project['owner'],'Real planning needs a configured project owner')
            require(not any(x.get('synthetic',False) for x in [people_data,capacity,calendar]),'Real planning cannot use synthetic people/capacity/calendar')
            require(not any(e.get('synthetic',False) for e in evidence.values()),'Real planning cannot use synthetic evidence')
        require(isinstance(assess['ready_for_planning'],bool),'ready_for_planning must be boolean')
        require(assess['status'] in ['draft','baseline'],'Invalid assessment status')
        active=req['status'] != 'intake' or planning or assess['ready_for_planning']
        blocked=[]
        for q in questions.values():
            require(isinstance(q['blocking'],bool),f'{q["id"]}: blocking must be boolean')
            require(q['status'] in ['open','resolved'],f'{q["id"]}: invalid question status')
            require(bool(q.get('owner')),f'{q["id"]}: question needs owner')
            if q['status']=='resolved':
                require(bool(q.get('answer')) and bool(q.get('source')),f'{q["id"]}: resolution requires answer/source')
            if q['blocking'] and q['status']=='open': blocked.append(q['id'])
        for e in evidence.values():
            require(e['source_id'] in sources,f'{e["id"]}: unknown source')
            for field in ['path','source_revision','observed_at','claim']:
                require(bool(e.get(field)),f'{e["id"]}: missing {field}')
            require(e['state'] in ['CONFIRMED','ASSUMED','UNKNOWN'],f'{e["id"]}: invalid evidence state')
        for fact in req['facts']:
            require(fact['state'] in ['CONFIRMED','ASSUMED','UNKNOWN'],'Invalid fact state')
            require(bool(fact.get('evidence_ids')) or bool(fact.get('owner')),'Fact needs evidence or assumption owner')
            require(set(fact.get('evidence_ids',[])) <= evidence.keys(),'Unknown fact evidence ID')
        for item in ac.values():
            require(bool(item.get('statement')),f'{item["id"]}: missing acceptance statement')
            require(bool(item.get('requirement_ids')),f'{item["id"]}: no FR link')
            require(set(item.get('requirement_ids',[])) <= fr.keys(),f'{item["id"]}: unknown FR')
        if active:
            require(bool(ac) and bool(fr) and bool(wp),'Clarified assessment needs FR, AC and work packages')
            require(set(estimates)==set(wp),'Estimates must cover exactly the work package IDs')
        topological(packages)
        for p in wp.values():
            identifier=p['id']
            for field in ['name','complexity','deliverable','done_when']:
                require(bool(p.get(field)),f'{identifier}: missing {field}')
            require(p['work_type'] in types,f'{identifier}: unknown work_type')
            require(p['complexity'] in ['low','medium','high'],f'{identifier}: invalid complexity')
            require(bool(p['acceptance_ids']) and set(p['acceptance_ids']) <= ac.keys(),f'{identifier}: invalid AC references')
            require(set(p['evidence_ids']) <= evidence.keys(),f'{identifier}: unknown evidence ID')
            require(isinstance(p['priority'],int) and not isinstance(p['priority'],bool),f'{identifier}: priority must be integer')
            if p.get('not_before'): day(p['not_before'])
            owner=p.get('assigned_to')
            if owner:
                require(owner in people,f'{identifier}: unknown person')
                if owner in people:
                    require(set(p['skills']) <= set(people[owner]['skills']),f'{identifier}: person lacks required skills')
            if planning or assess['ready_for_planning']:
                require(owner in capacity['people'],f'{identifier}: no capacity for assignment')
        for e in estimates.values():
            identifier=e['id']; values=e['effort_pd']
            require(identifier in wp,f'{identifier}: estimate has no WP')
            valid=all(number(values.get(k)) and values[k]>0 for k in ['low','expected','high'])
            require(valid,f'{identifier}: effort must be finite positive numbers')
            if valid: require(values['low']<=values['expected']<=values['high'],f'{identifier}: unordered effort scenarios')
            require(e['basis'] in ['historical-range','expert-judgement'],f'{identifier}: invalid estimate basis')
            require(bool(e.get('rationale')),f'{identifier}: estimate rationale missing')
            require(e['confidence'] in ['low','medium','high'],f'{identifier}: invalid confidence')
            refs=e['historical_refs']
            require(set(refs)<=historical.keys(),f'{identifier}: unknown historical reference')
            if e['basis']=='historical-range':
                minimum=load(root/'planning/estimation-rules.yaml')['minimum_analogues']
                require(len(set(refs))>=minimum,f'{identifier}: historical basis needs at least {minimum} distinct references')
            if not req.get('synthetic',False):
                require(not any(historical[h].get('synthetic',False) for h in refs if h in historical),f'{identifier}: synthetic history cannot estimate a real project')
            for rid in e.get('risk_ids',[]):
                require(rid in risks and risks[rid]['treatment']=='effort-included',f'{identifier}: invalid included risk')
        for r in risks.values():
            require(r['probability'] in ['low','medium','high'] and r['impact'] in ['low','medium','high'],f'{r["id"]}: invalid risk rating')
            require(bool(r.get('owner')) and bool(r.get('trigger')) and bool(r.get('mitigation')),f'{r["id"]}: risk owner/trigger/mitigation missing')
            require(bool(r['affected_work']) and set(r['affected_work'])<=wp.keys(),f'{r["id"]}: invalid affected work')
            require(r['treatment'] in ['effort-included','calendar-gate','monitor-only'],f'{r["id"]}: invalid risk treatment')
            if r['treatment']=='effort-included':
                require(any(r['id'] in e.get('risk_ids',[]) for e in estimates.values()),f'{r["id"]}: included risk has no estimate mapping')
            if r['treatment']=='calendar-gate':
                require(any(wp[w].get('not_before') for w in r['affected_work'] if w in wp),f'{r["id"]}: calendar risk has no not_before gate')
        links=data['traceability.yaml']['links']; coverage=set()
        for link in links:
            aid=link['acceptance_id']; coverage.add(aid)
            require(aid in ac,'Unknown traceability AC')
            require(bool(link['work_packages']) and set(link['work_packages'])<=wp.keys(),'Invalid traceability WP')
            require(link['test_status'] in ['planned','passed','failed'],'Invalid test status')
            if link['test_status']=='passed': require(bool(link.get('test_evidence')),'Passed AC needs test evidence')
            for w in link['work_packages']:
                if w in wp: require(aid in wp[w]['acceptance_ids'],f'{w}: traceability differs from WBS')
        if active: require(coverage==set(ac),'Traceability must cover every AC')
        if planning or assess['ready_for_planning']:
            require(not blocked,f'Open blocking questions: {blocked}')
            require(assess['ready_for_planning'],'Assessment not ready for planning')
            require(bool(assess.get('reviewed_by')) and bool(assess.get('reviewed_at')),'Readiness requires review metadata')
            require(bool(assess.get('assumptions')),'Ready assessment must disclose assumptions')
        if assess['status']=='baseline' or req['status']=='baseline':
            require(bool(assess.get('owner_confirmation')),'Baseline requires owner_confirmation')
        for person,c in capacity['people'].items():
            require(person in people,f'Capacity refers to unknown person {person}')
            require(number(c['fraction']) and 0<c['fraction']<=1,f'{person}: capacity fraction must be in (0,1]')
            for value in c.get('leave',[]): day(value)
        scheduling = planning or assess['ready_for_planning']
        if scheduling:
            require(bool(capacity.get('valid_from')) and bool(capacity.get('valid_until')),'Scheduling requires capacity validity dates')
            require(bool(calendar.get('start_date')),'Scheduling requires a start_date')
            require(bool(calendar.get('work_weekdays')),'Scheduling requires work_weekdays')
        if capacity.get('valid_from') and capacity.get('valid_until'):
            require(day(capacity['valid_from'])<=day(capacity['valid_until']),'Invalid capacity window')
        require(isinstance(calendar['work_weekdays'],list) and all(type(x) is int and 0<=x<=6 for x in calendar['work_weekdays']),'Invalid work_weekdays')
        for value in calendar.get('holidays',[]): day(value)
        if calendar.get('start_date'): day(calendar['start_date'])
    except (KeyError,TypeError,ValueError,AttributeError) as exc:
        errors.append(f'Malformed artifact: {exc}')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true'); group.add_argument('--requirement')
    parser.add_argument('--planning',action='store_true')
    args=parser.parse_args()
    dirs=sorted((args.root/'requirements').glob('REQ-*')) if args.all else [requirement_dir(args.root,args.requirement)]
    failures=[]
    # Parse every YAML as a basic repo-wide syntax check, including Skill metadata.
    for path in args.root.rglob('*.yaml'):
        if '.venv' in path.parts or '.git' in path.parts: continue
        try: load(path)
        except Exception as exc: failures.append(f'{path.relative_to(args.root)}: {exc}')
    for directory in dirs:
        failures += [f'{directory.name}: {e}' for e in validate(args.root,directory,args.planning)]
    if failures:
        print('\n'.join(f'ERROR {e}' for e in failures)); return 1
    print(f'OK: YAML syntax and {len(dirs)} requirement artifact sets'); return 0
if __name__=='__main__':
    raise SystemExit(main())
