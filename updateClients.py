#!/usr/bin/env python3

import os
import subprocess
import fnmatch
import argparse

targets = ['neat-la1', 'neat-la2', 'neat-ec1', 'neat-ec2', 'neat-ny1']

# discretely handle each type or combos thereof
parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="show output without running", action="store_true")
parser.add_argument("--deleg", help="Delegates SQLite db", action="store_true")
parser.add_argument("--docs", help="NEAT docs", action="store_true")
parser.add_argument("--hist", help="historical data", action="store_true")
parser.add_argument("--persist", help="jdbc persistence xml", action="store_true")
parser.add_argument("--sim", help="sim data", action="store_true")
parser.add_argument("--skip", help="csv list of servers to skip", metavar="neat-la1,neat-la2")
parser.add_argument("--tc", help="tom cat", action="store_true")
parser.add_argument("--web", help="web apps", action="store_true")
args = parser.parse_args()

ELECTIONS = "/data/development"

DATASRC = "{0}/data/".format(ELECTIONS)
DATATARG = DATASRC

SQLDATASRC = "{0}/primaries/db/delegates".format(ELECTIONS)
SQLDATATARG = SQLDATASRC

TCSRC = "{0}/apache-tomcat-8.0.30/webapps/".format(ELECTIONS)
TCTARGNEW = "{0}/apache-tomcat-8.0.30/webapps".format(ELECTIONS)
TCTARGOLD = "{0}/apache-tomcat-8.0.26/webapps".format(ELECTIONS)

WEBSRC = "/opt/www/webserver/2.4.10/htdocs/"
WEBTARGNEW = "/var/www/html"
WEBTARGOLD = WEBSRC

NEATDOCSSRC = "/opt/www/webserver/2.4.10/htdocs/neat/docs"
NEATDOCSTARGNEW = "/var/www/html/neat/docs"
NEATDOCSTARGOLD = NEATDOCSSRC

# default all active list
active = {'neat-la1': 'Y', 'neat-la2': 'Y', 'neat-ec1': 'Y', 'neat-ec2': 'Y', 'neat-ny1': 'Y'}

tctargmap = {'neat-la1': TCTARGNEW, 'neat-la2': TCTARGNEW, 'neat-ec1': TCTARGNEW,
             'neat-ec2': TCTARGNEW, 'neat-ny1': TCTARGOLD}

webtargmap = {'neat-la1': WEBTARGNEW, 'neat-la2': WEBTARGNEW, 'neat-ec1': WEBTARGNEW,
              'neat-ec2': WEBTARGNEW, 'neat-ny1': WEBTARGOLD}

datatargmap = {'neat-la1': DATATARG, 'neat-la2': DATATARG, 'neat-ec1': DATATARG,
               'neat-ec2': DATATARG, 'neat-ny1': DATATARG}

sqltargmap = {'neat-la1': SQLDATATARG, 'neat-la2': SQLDATATARG, 'neat-ec1': SQLDATATARG,
              'neat-ec2': SQLDATATARG, 'neat-ny1': SQLDATATARG}

docstargmap = {'neat-la1': NEATDOCSTARGNEW, 'neat-la2': NEATDOCSTARGNEW, 'neat-ec1': NEATDOCSTARGNEW,
               'neat-ec2': NEATDOCSTARGNEW, 'neat-ny1': NEATDOCSTARGOLD}

# take out requested downed nodes
if args.skip:
    skipList = args.skip.split(",")
    for downNode in skipList:
        if downNode in active:
            active[downNode] = 'N'


def genPipeMatches(dirs, patterns):
    pipeDict = {}
    for p in patterns:
        for dir in fnmatch.filter(dirs, p):
            pipeDict[dir] = 1
    return list(pipeDict.keys())


# dynamically obtain src files or directories
def findDirs(dir, pattern, level, isDir):
    filematches = []
    for root, dirs, files in os.walk(dir):
        curlevel = (root if root == dir else root + os.sep).replace(dir, '').count(os.sep)
        if curlevel == level:
            found = []
            try:
                if pattern.index("|", 0) != 0:
                    found = genPipeMatches(dirs if isDir else files, pattern.split("|"))
            except ValueError:
                found = fnmatch.filter(dirs if isDir else files, pattern)
            for d in found:
                filematches += [root + d]
    return filematches


# invoke the rsync or plain echo params
def syncLoop(srcList, node, targetmap, isDebug, opts):
    print('rsyncing...' + node)
    for src in srcList:
        target = "{0}.inbcu.com:{1}".format(node, targetmap[node])
        params = ['rsync', src, target]
        for opt in opts:
            params.insert(1,opt)
        if isDebug:
            params.insert(1, '-n')
        try:
            output = subprocess.check_output(params, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        outList = output.decode("utf-8").split("\n")
        for line in outList:
            print(line)
    print('rsynced to ' + node)


tcWARs = sorted(findDirs(TCSRC, '*war', 0, False))
httpds = sorted(findDirs(WEBSRC, '*', 0, True))
httpdsELECT = sorted(findDirs(WEBSRC, 'editorial|tally_sheet|launcher', 0, True))
historicalDataFolders = sorted(findDirs(DATASRC, '20??-??-??', 0, True))
simDataFolders = sorted(findDirs(DATASRC, 'S0??~????-??-??', 0, True))

baseOpts = ['-avz', '-t']

# for all hosts
for host in targets:
    if active[host] == 'Y':
        # handle tom cat app server
        if args.tc:
            syncLoop(tcWARs, host, tctargmap, args.debug, baseOpts + ['--include=tally_sheet', '--exclude=neat'])

        # handle apache httpd server
        if args.web:
            if host.endswith("1") or (host == 'neat-la2'):
                syncLoop(httpdsELECT, host, webtargmap, args.debug, baseOpts + ['--exclude=neat'])
            else:
                syncLoop(httpds, host, webtargmap, args.debug, baseOpts + ['--exclude=neat'])

        # handle historical data
        if args.hist:
            syncLoop(historicalDataFolders, host, datatargmap, args.debug, baseOpts)

        # handle sim data
        if args.sim:
            syncLoop(simDataFolders, host, datatargmap, args.debug, baseOpts)

        # handle SQLite db
        if args.deleg:
            syncLoop([SQLDATASRC], host, sqltargmap, args.debug, baseOpts)

        # handle NEAT docs
        if args.docs:
            syncLoop([NEATDOCSSRC], host, docstargmap, args.debug, baseOpts)
    else:
        print(host + ' not active')
