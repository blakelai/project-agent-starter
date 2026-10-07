"""Close only after recorded delivery evidence, human acceptance and closure decision pass validation."""
import argparse
from pathlib import Path
from common import ROOT, load, write, requirement_dir
from validate import validate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT); parser.add_argument('--requirement',required=True)
    args=parser.parse_args(); directory=requirement_dir(args.root,args.requirement)
    errors=validate(args.root,directory,stage='closure')
    if errors: raise SystemExit('\n'.join(errors))
    req=load(directory/'requirement.md'); req['status']='closed'; write(directory/'requirement.md',req)
    print(f'Closed {args.requirement} using existing human acceptance records')


if __name__=='__main__': main()
