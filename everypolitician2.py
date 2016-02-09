#!/usr/bin/env python3

# Converts our data into CSV files for everypolitician.org,
# one file for the House and one file for the Senate.
#
# Usage:
# python everypolitician.py outputbasename/
#
# Which will write:
# outputbasename/house.csv
# outputbasename/senate.csv

import sys, csv, argparse

from utils import yaml_load, CURRENT_CONGRESS, states

govtrackdir='/home/hkatz/workspace-nbc/Projects/CPLD/CPD/DATA/govtrack/congress-legislators/'

def run():
    parser = argparse.ArgumentParser(description='handle legis/exec')
    parser.add_argument('destdir')
    parser.add_argument('--inpType')
    args = parser.parse_args()
    if len(sys.argv) < 2:
        print("Usage: python everypolitician.py outputbasename/")
        sys.exit(0)

    # Load current legislators.
    if args.inpType == 'leg':
        data = yaml_load("{0}/legislators-current.yaml".format(govtrackdir))
    else:
        data = yaml_load("{0}/executive.yaml".format(govtrackdir))
    data_social_media = {}
    for legislator in yaml_load("{0}/legislators-social-media.yaml".format(govtrackdir)):
        data_social_media[legislator['id']['bioguide']] = legislator

    # Create output files.
    if args.inpType == 'leg':
        writers = {
            "rep": csv.writer(open(args.destdir + "house.csv", "w")),
            "sen": csv.writer(open(args.destdir + "senate.csv", "w")),
        }
    else:
        writers = {
            "prez": csv.writer(open(args.destdir + "prez.csv", "w")),
            "viceprez": csv.writer(open(args.destdir + "viceprez.csv", "w"))
        }

    for w in writers.values():
        w.writerow([
            "id",
            # "name",
            "postal_code",
            "state",
            # "group",
            "class_district",
            "start_date",
            "end_date",
            "num_terms",
            "party",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
            # "sort_name",
            # "phone",
            "gender",
            # "birth_date",
            "image",
            # "twitter",
            # "facebook",
            # "instagram",
            # "wikipedia",
            # "website",
            "office_code",
            "office_name"
        ])

    # Write out one row per legislator for their current term.
    for legislator in data:
        genRow(legislator, writers)

def genRow(legislator, writers):
    term = legislator['terms'][-1]
    allTerms = legislator['terms']
    # TODO: "If someone changed party/faction affilation in the middle of the term, you should include two entries, with the relevant start/end dates set."
    if 'party' in term:
        legisParty = term['party']
    else:
        legisParty = "N/A"
    if 'bioguide' in legislator['id']:
        bioguide = legislator['id']['bioguide']
    else:
        bioguide = 'bioguide N/A'
    termNdx = 1
    if len(allTerms) > 1:
        for curTerm in allTerms:
            legisType, officeCode, officeName, state, stateLong = getByType(curTerm)
            startTerm = curTerm['start']
            endTerm = curTerm['end']
            numTerms = termNdx
            termNdx += 1
            w = writers[curTerm['type']]
            writeRow(endTerm, legisParty, legisType, legislator, numTerms, startTerm, term, w, bioguide, state, stateLong,
                     officeCode, officeName)
    else:
        legisType, officeCode, officeName, state, stateLong = getByType(term)
        startTerm = term['start']
        endTerm = term['end']
        numTerms = 1
        w = writers[term['type']]
        writeRow(endTerm, legisParty, legisType, legislator, numTerms, startTerm, term, w, bioguide, state, stateLong,
                 officeCode, officeName)


def getByType(term):
    if term['type'] == 'sen':
        legisType = term['class']
        state = term['state']
        stateLong = states[term['state']]
        officeCode = "S"
        officeName = "Senate"
    elif term['type'] == 'rep':
        legisType = term['district']
        state = term['state']
        stateLong = states[term['state']]
        officeCode = "H"
        officeName = "House"
    else:
        legisType = term['how']
        state = 'US'
        stateLong = 'United States'
        officeCode = "P"
        officeName = "Executive"
    return legisType, officeCode, officeName, state, stateLong


def writeRow(endTerm, legisParty, legisType, legislator, numTerms, startTerm, term, w, bioguide, state, stateLong,
             officeCode, officeName):
    w.writerow([
        bioguide,
        # build_name(legislator, term, 'full'),
        state,  # build_area(term),
        stateLong,
        # term['party'],
        legisType,
        startTerm,
        endTerm,
        numTerms,
        legisParty,
        legislator['name'].get('first'),
        legislator['name'].get('middle') if 'middle' in legislator['name'] else '',
        legislator['name'].get('last'),
        legislator['name'].get('suffix'),
        # build_name(legislator, term, 'sort'),
        # term.get('phone'),
        legislator['bio'].get('gender'),
        # legislator['bio'].get('birthday'),
        "https://theunitedstates.io/images/congress/original/%s.jpg" % bioguide,
        # data_social_media.get(legislator['id']['bioguide'], {}).get("social", {}).get("twitter"),
        # data_social_media.get(legislator['id']['bioguide'], {}).get("social", {}).get("facebook"),
        # data_social_media.get(legislator['id']['bioguide'], {}).get("social", {}).get("instagram"),
        # legislator['id'].get('wikipedia', '').replace(" ", "_"),
        # term['url'],
        officeCode,
        officeName
    ])


ordinal_strings = {1: "st", 2: "nd", 3: "rd", 11: 'th', 12: 'th', 13: 'th'}


def ordinal(num):
    return str(num) + ordinal_strings.get(num % 100, ordinal_strings.get(num % 10, "th"))


def build_area(term):
    # Builds the string for the "area" column, which is a human-readable
    # description of the legislator's state or district.
    ret = states[term['state']]
    if term['type'] == 'rep':
        ret += "’s "
        if term['district'] == 0:
            ret += "At-Large"
        else:
            ret += ordinal(term['district'])
        ret += " Congressional District"
    return ret


def build_name(p, t, mode):
    # Based on:
    # https://github.com/govtrack/govtrack.us-web/blob/master/person/name.py

    # First name.
    firstname = p['name']['first']
    if firstname.endswith('.'):
        if 'middle' in p['name']:
            firstname = p['name']['middle']
        else:
            firstname = p['name']['first']
        # firstname = p['name']['middle']
    if p['name'].get('nickname') and len(p['name']['nickname']) < len(firstname):
        firstname = p['name']['nickname']

    # Last name.
    lastname = p['name']['last']
    if p['name'].get('suffix'):
        lastname += ', ' + p['name']['suffix']

    if mode == "full":
        return firstname + ' ' + lastname
    elif mode == "sort":
        return lastname + ', ' + firstname
    else:
        raise ValueError(mode)


if __name__ == '__main__':
    run()
