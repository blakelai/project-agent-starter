"""Project scope and combined requirement inputs. Uses one capacity pool for every selected REQ."""
from copy import deepcopy
from pathlib import Path
import re

from common import index, load, requirement_dir, topological
from glossary import input_paths as term_inputs, require, text
from validate import validate


def project_dir(root, identifier):
    require(isinstance(identifier,str) and re.fullmatch(r'PROJ-[A-Za-z0-9][A-Za-z0-9-]{0,63}',identifier), 'Invalid PROJ ID')
    path = Path(root).resolve()/'vault/projects'/identifier
    require(path.resolve()==path, 'Project path must not traverse symlinks')
    return path


def requirement_inputs(root, directory):
    root = Path(root).resolve()
    paths = {f'{directory.name}:{p.name}':p for p in directory.glob('*.md')
             if not p.name.startswith(('schedule-', 'forecast-', 'progress-report')) and p.name!='index.md'}
    # Requirement-local attachments and nested decision notes are evidence inputs too.
    for path in directory.rglob('*'):
        relative = path.relative_to(directory)
        if len(relative.parts) > 1 and path.is_file() and not any(part.startswith('.') for part in relative.parts):
            paths[f'{directory.name}:{relative.as_posix()}'] = path
    req = load(directory/'requirement.md')
    for doc in req.get('source_documents',[]):
        paths['brd:'+doc['id']] = root/doc['path']
        for asset in doc['assets']:
            paths['asset:'+asset['path']] = root/asset['path']
    paths.update(term_inputs(root, req))
    return paths


def collect(root, identifier, forecast=False):
    root = Path(root).resolve(); directory = project_dir(root, identifier)
    manifest = load(directory/'project.md')
    require(manifest.get('schema_version') == 1, 'Unsupported project schema')
    require(manifest['id']==identifier, 'Project ID must match directory')
    require(all(text(manifest.get(k)) for k in ['name','owner','goal']) and manifest.get('success_criteria') and manifest.get('scope'),
            'Project planning needs name, owner, goal, success_criteria and scope')
    for field in ['success_criteria', 'scope', 'non_goals']:
        require(isinstance(manifest.get(field), list) and all(text(value) for value in manifest[field]),
                f'Project {field} must be a list of non-empty strings')
    selected = index(manifest['requirements'], 'project requirements')
    require(bool(selected), 'Project has no selected requirements')
    packages, estimates, progress, inputs, priorities = [], [], {}, {}, {}
    inputs['project_manifest'] = directory/'project.md'
    for path in (root/'vault/planning').glob('*.md'):
        if path.name != 'index.md': inputs['planning:'+path.stem] = path
    inputs['project_config'] = root/'vault/config/project.md'
    inputs['sources'] = root/'vault/knowledge/sources.md'
    for req_id, selection in selected.items():
        require(type(selection['priority']) is int, 'Requirement priority must be an integer')
        req_dir = requirement_dir(root, req_id)
        require(req_dir.resolve()==req_dir, 'Requirement path must not traverse symlinks')
        errors = validate(root, req_dir, planning=True, stage='delivery' if forecast else 'planning')
        require(not errors, req_id+': '+'; '.join(errors))
        req = load(req_dir/'requirement.md')
        require(forecast or req['status']!='closed', 'Closed requirements belong in historical/forecast scope, not new full-work schedules')
        inputs.update(requirement_inputs(root, req_dir))
        for original in load(req_dir/'work-breakdown.md')['work_packages']:
            wp = deepcopy(original); identifier_wp = req_id+'/'+wp['id']
            priorities[identifier_wp] = (selection['priority'], wp['priority'], identifier_wp)
            wp['id'] = identifier_wp
            wp['depends_on'] = [req_id+'/'+dependency for dependency in wp['depends_on']]
            wp.update(requirement_id=req_id, work_package_id=original['id'])
            packages.append(wp)
        for original in load(req_dir/'estimation.md')['estimates']:
            est = deepcopy(original); est['id'] = req_id+'/'+est['id']; estimates.append(est)
        if forecast:
            progress[req_id] = load(req_dir/'progress.md')
    by_id = index(packages, 'combined work')
    for dependency in manifest.get('dependencies',[]):
        def key(endpoint):
            require(endpoint['requirement_id'] in selected, 'Cross-REQ dependency must be in project scope')
            result=endpoint['requirement_id']+'/'+endpoint['work_package_id']
            require(result in by_id, 'Unknown cross-REQ work package')
            return result
        before, after = key(dependency['predecessor']), key(dependency['successor'])
        if before not in by_id[after]['depends_on']: by_id[after]['depends_on'].append(before)
    order = {identifier_wp:rank for rank,identifier_wp in enumerate(sorted(priorities,key=priorities.get))}
    for wp in packages: wp['priority'] = order[wp['id']]
    topological(packages)
    return manifest, packages, estimates, progress, inputs
