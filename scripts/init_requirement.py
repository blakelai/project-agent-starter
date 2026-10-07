"""Create an intake from templates without overwriting an existing requirement."""
import argparse
import shutil
import os
from pathlib import Path
from urllib.parse import quote
from common import ROOT, requirement_dir, load, write, index
from okf import write_directory_index
from brd import capture_brd, registered_sources, pending_coverage

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id'); parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--source', action='append', default=[], metavar='BRD_PATH',
                        help='Repository-relative BRD Markdown path; repeat for multiple documents')
    args=parser.parse_args(); target=requirement_dir(args.root,args.id)
    if target.exists(): raise SystemExit(f'Refusing to overwrite {args.id}')
    try:
        documents=[capture_brd(args.root, source) for source in args.source]
        index(documents, 'BRD sources')
        registry=registered_sources(args.root, documents) if documents else None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(str(exc))
    shutil.copytree(args.root/'vault/templates/requirement',target)
    for path in target.rglob('*'):
        if path.is_file() and path.suffix == '.md':
            path.write_text(path.read_text(encoding='utf-8').replace('{{REQ_ID}}',args.id),encoding='utf-8')
    if documents:
        req=load(target/'requirement.md'); req['source_documents']=documents; write(target/'requirement.md',req)
        trace=load(target/'traceability.md'); trace['source_coverage']=pending_coverage(documents)
        write(target/'traceability.md',trace)
        with (target/'requirement.md').open('a',encoding='utf-8') as stream:
            stream.write('\n## 原始需求來源\n\n')
            for doc in documents:
                relative=quote(os.path.relpath(args.root/doc['path'], target).replace(os.sep,'/'),safe='/')
                stream.write(f'- [{doc["id"]}]({relative})\n')
        write(args.root/'vault/knowledge/sources.md',registry)
    write_directory_index(target, args.id)
    write_directory_index(target.parent, '需求')
    print(f'Created intake {args.id}; resolve scope/evidence before assessment or scheduling')
if __name__=='__main__': main()
