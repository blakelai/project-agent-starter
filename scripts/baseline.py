"""Preview, record an explicitly approved exact project snapshot, or verify a saved baseline."""
import argparse
from pathlib import Path
import re
import shutil
import tempfile

from common import ROOT, digest, load, write
from delivery import approval
from glossary import require, revision
from okf import write_directory_index
from project import project_dir, collect


def baseline_dir(root, project_id, version):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{0,63}',version) and version not in {'.','..'}, 'Invalid baseline version')
    path=project_dir(root,project_id)/'baseline'/version
    require(path.resolve()==path, 'Baseline path must not traverse symlinks')
    return path


def preview(root, project_id, report_name):
    root=Path(root).resolve(); directory=project_dir(root,project_id)
    require(re.fullmatch(r'(schedule|forecast)-(low|expected|high)\.md',report_name), 'Invalid report filename')
    report=directory/report_name
    require(report.resolve()==report, 'Report path must not traverse symlinks')
    result=load(report)
    require(result['project_id']==project_id, 'Report project mismatch')
    _,_,_,_,inputs=collect(root,project_id,forecast=report_name.startswith('forecast-'))
    expected={p.relative_to(root).as_posix():digest(p) for p in inputs.values()}
    require(result['input_sha256']==expected, 'Report inputs changed; recalculate and obtain confirmation for the new version')
    expected[report.relative_to(root).as_posix()]=digest(report)
    return expected,revision(expected)


def create(root, project_id, version, report_name, expected_revision, by, at, source):
    root=Path(root).resolve(); target=baseline_dir(root,project_id,version)
    require(not target.exists(), 'Refusing to overwrite a baseline')
    decision={'by':by,'at':at,'source':source}; approval(decision)
    files,current=preview(root,project_id,report_name)
    require(current==expected_revision, 'Baseline changed since human review')
    for name in files:
        path=root/name
        require(path.resolve().is_relative_to(root/'vault'), 'Snapshot input must stay within vault')
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.baseline-',dir=target.parent) as staging:
        staging=Path(staging)
        for name,expected in files.items():
            destination=staging/'snapshot'/name; destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(root/name,destination)
            require(digest(destination)==expected, 'Input changed while creating baseline')
        write(staging/'baseline.md',{'schema_version':1,'project_id':project_id,'version':version,
              'report':report_name,'revision':current,'confirmation':decision,'files':files})
        write_directory_index(staging,version)
        staging.rename(target)
    write_directory_index(target.parent,'基準版本')
    write_directory_index(target.parent.parent,project_id)
    return target


def verify(root, project_id, version):
    directory=baseline_dir(root,project_id,version); manifest=load(directory/'baseline.md')
    require(manifest['project_id']==project_id and manifest['version']==version, 'Baseline identity mismatch')
    approval(manifest['confirmation'])
    require(manifest['revision']==revision(manifest['files']), 'Baseline manifest changed')
    for name,expected in manifest['files'].items():
        path=(directory/'snapshot'/name).resolve()
        require(path.is_relative_to(directory/'snapshot') and path.is_file(), 'Missing or out-of-bounds snapshot file')
        require(digest(path)==expected, f'Baseline content changed: {name}')
    actual={p.relative_to(directory/'snapshot').as_posix() for p in (directory/'snapshot').rglob('*') if p.is_file()}
    require(actual==set(manifest['files']), 'Unexpected baseline snapshot files')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['preview','create','verify']:
        sub=commands.add_parser(name); sub.add_argument('--project',required=True)
        if name!='verify': sub.add_argument('--report',default='schedule-expected.md')
        if name!='preview': sub.add_argument('--version',required=True)
        if name=='create':
            for arg in ['revision','by','at','source']: sub.add_argument('--'+arg,required=True)
    args=parser.parse_args()
    try:
        if args.command=='preview':
            files,current=preview(args.root,args.project,args.report)
            print(f'{current}\n{len(files)} files; review {args.report} and inputs before human confirmation')
        elif args.command=='create':
            print(create(args.root,args.project,args.version,args.report,args.revision,args.by,args.at,args.source))
        else:
            verify(args.root,args.project,args.version); print('Baseline snapshot hashes verified')
    except (OSError,KeyError,TypeError,ValueError,AttributeError) as exc:
        raise SystemExit(str(exc))


if __name__=='__main__': main()
