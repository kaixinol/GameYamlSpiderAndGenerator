#!/usr/bin/python
# -*- coding: utf-8 -*-
from github import Github
import sys
import steam
import hashlib
import time
import ruamel
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString as pss

md5 = lambda n: hashlib.md5(n.encode()).hexdigest()[8:-8].lower()

g1 = Github('token')
repo = g1.get_repo('kaixinol/games')
stm = steam.IsSteam('https://github.com/FurryGamesIndex/games/issues/'
                    + sys.argv[1])
stmData = steam.GetSteamData(stm)

if stm != None:
    stmName = stm.split("/")[5]
# create new branch
    sb = repo.get_branch('ghnmsl')
    repo.create_git_ref(ref='refs/heads/' + md5(stmName),
                        sha=sb.commit.sha)

# push files

    str_arr = stmData[1][stmData[1].rfind('.'):]
    with open(f'thumbnail{str_arr}',"rb") as fd:                   # 打开二进制文件
     img_data=fd.read() 
    repo.create_file(f'assets/{stmName}/thumbnail{str_arr}',
                     f'assets: games/{stmName}: add thumbnail file',
                     img_data, branch=md5(stmName))
    print(repo.create_file('games/{}.yaml'.format(stmName), 'games/{}: new game'.format(stmName), ruamel.yaml.YAML(typ=['rt', 'string']).dump_to_string(stmData[0]),branch=md5(stmName)))
    time.sleep(3)

# create PR

    fgi = g1.get_organization('FurryGamesIndex').get_repo('games')
    pr = fgi.create_pull('[DO NOT MERGE]games/{}: new game'.format(stmName), 'Created by my bot'
                         , 'master',
                         'kaixinol:{}'.format(md5(stmName)), True)

 # comment

    issue = fgi.get_issue(number=int(sys.argv[1]))
    #issue.create_comment('PR Opened on #{}\n'.format(str(pr.number)))
