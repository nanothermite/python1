#!/usr/bin/env python3

import re
import sys


def toabbrev(x):
    return mapping[x]


def identity(x):
    return x


def isabbrev(x):
    return len(mapping[x] if int(year) > 1960 and x in mapping else x) == 2


def isdigit(x):
    pattern = re.compile('^\d+$')
    return pattern.search(x) is not None


def makedict(states, statevals):
    statecounts = list(filter(isdigit, statevals.rstrip('\n').split(',')))
    lastval = statecounts.pop()
    print("got {0} values: {1}".format(len(statecounts), ','.join(statecounts)))
    return (lastval, dict(zip(states, statecounts)))


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
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    'Wyoming' :		    'WY'
}
states = []
counts = []
ecDict = {}
total = 0
baseYear = 1789
isData = False
for line in lines:
    try:
        totPos = line.index('Total')
        if totPos > 0:
            states = list(map(toabbrev if int(year) > 1960 else identity, filter(isabbrev, line.rstrip('\n').split(','))))
            # print("got {0} states: {1}".format(len(states), ','.join(states)))
        elif totPos == 0:
            if line.endswith('Total'):
                isData = True
            else:
                (total, ecDict) = makedict(states, line)
    except ValueError:
        if int(year) > 1960:
            if re.compile('Electoral Vote').search(line) is not None:
                (total, ecDict) = makedict(states, line)
                break
        if isData:
            (total, ecDict) = makedict(states, line)
            break
        else:
            print(".", end='')

term = int((int(year) - baseYear + 1)/4) + 1
for k, v in ecDict.items():
    print("{0},{1},{2},{3},{4},{5}".format(year, int(year) + 1, int(year) + 5, term, k, v))
# print("total {0} for {1}".format(total, year))

