#!/usr/bin/env python3

import re
import sys


def toabbrev(x):
    return mapping[x]


def identity(x):
    return x


def makedigit(x):
    return 0 if x == '-' else int(x)


def isabbrev(x):
    return len(mapping[x] if int(year) > 1960 and x in mapping else x) == 2


def dumpdict(topdict, dicttype):
    for cand, votedict in topdict.items():
        candparts = cand.split(' ')
        for state, count in votedict.items():
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(year, int(year) + 1, int(year) + 5,
                                                           candparts[0],
                                                           "" if len(candparts) == 2 else candparts[1].replace('.', ''),
                                                           candparts[len(candparts) - 1],
                                                           state, count, dicttype))


def checkpattern(pattern, target):
    return pattern.search(target) is not None


file = sys.argv[1]
year = file.split('/').pop().split('.')[0]
with open(file, 'r') as f:
    lines = f.read().splitlines()

# for all lines

mapping = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
states = []
presDict = {}
veepDict = {}
baseYear = 1789
seenPres = True if int(year) < 1964 else False
seenVicePres = False

# get first line to determine states
states = list(map(toabbrev if int(year) > 1960 else identity,
                  filter(isabbrev, lines[0].rstrip('\n').split(','))))

# scan remaining files for lines beginning with For or "
quotepattern = re.compile('^,"|^For') if int(year) > 1960 else re.compile('^"')
forpattern = re.compile('^For')
veeppattern = re.compile('Vice-President')
prezpattern = re.compile(' President')
namepattern = re.compile(',"([\w,\.\s\*]+)",') if int(year) > 1960 else re.compile('^"([\w,\.\s\*]+)",')
skipquotepattern = re.compile('^"\*')

for line in lines:
    try:
        if skipquotepattern.search(line) is not None:
            continue
        elif quotepattern.search(line) is not None:
            nameparts = namepattern.split(line)
            if nameparts is not None:
                if int(year) > 1960 and nameparts[0].startswith('For'):
                    seenVicePres = checkpattern(veeppattern, nameparts[0])
                    seenPres = checkpattern(prezpattern, nameparts[0])
                candname = nameparts[1].split(',')[0]
                candvotes = list(map(makedigit, nameparts[2].rstrip('\n').split(',')))
                if seenVicePres:
                    veepDict[candname] = dict(zip(states, candvotes))
                else:
                    presDict[candname] = dict(zip(states, candvotes))
        elif forpattern.search(line) is not None:
            seenVicePres = checkpattern(veeppattern, line)
            seenPres = checkpattern(prezpattern, line)
    except ValueError:
        print(".", end='')

term = int((int(year) - baseYear + 1)/4) + 1
dumpdict(presDict, 'President')
if len(veepDict.keys()) > 0:
    dumpdict(veepDict, 'Vice-President')
