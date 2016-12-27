#!/usr/bin/python2.7
'''
One by one, fetch profile pages for OKCupid users. The input to this script
is a file with a list of usernames of profiles to pull,

Original version created on Jun 25, 2012

@author: Everett Wetchler (evee746)
'''

import csv
import datetime
import random
import sys
import time
import json
import copy

from BeautifulSoup import BeautifulSoup, UnicodeDammit
import gflags
import requests

DEFAULT_COOKIE = '16993350334538082753%3a15129489039068961025'
FLAGS = gflags.FLAGS
gflags.DEFINE_string('outfile', 'profiles.csv', 'Filename for output')
gflags.DEFINE_string('outfile2', 'essays.csv', 'Filename for output')
gflags.DEFINE_string('outfile3', 'languages.csv', 'Filename for output')
gflags.DEFINE_string('outfile4', 'photos.csv', 'Filename for output')
gflags.DEFINE_string('outfile5', 'lookingFors.csv', 'Filename for output')
gflags.DEFINE_string('outfile6', 'ethnicities.csv', 'Filename for output')
gflags.DEFINE_boolean('pull_essays', False,
                      'If True, pulls free responses sections. If False, '
                      'just basic profile details.')
gflags.DEFINE_string('session_cookie', DEFAULT_COOKIE, '')
gflags.DEFINE_string(
    'usernames_file', 'usernames.csv', 'File with usernames to fetch')
gflags.DEFINE_string(
    'completed_usernames_file', 'completed_usernames.csv',
    'File with usernames we have already fetched')


SLEEP_BETWEEN_QUERIES = 2
PROFILE_URL = "http://www.okcupid.com/profile/%s"


def pull_profile_and_essays(username):
    '''Given a username, fetches the profile page and parses it.'''
    url = PROFILE_URL % username
    print "Fetching profile HTML for", username + "... ",
    html = None
    for i in range(3):
        if i > 0:
            print "Retrying...",
        try:
            r = requests.get(url, cookies={'session': FLAGS.session_cookie})
            if r.status_code != 200:
                print "Error, HTTP status code was %d, not 200" % r.status_code
            else:
                html = r.content
                break
        except requests.exceptions.RequestException, e:
            print "Error completing HTTP request:", e
    if not html:
        print "Giving up."
        return None, None
    print "Parsing..."
    profile, userExtraInfo = parse_profile_html(html)
    return profile, userExtraInfo


def parse_profile_html(html):
    '''Parses a user profile page into the data fields and essays.

    It turns out parsing HTML, with all its escaped characters, and handling
    wacky unicode characters, and writing them all out to a CSV file (later),
    is a pain in the ass because everything that is not ASCII goes out of its
    way to make your life hard.

    During this function, we handle unescaping of html special
    characters. Later, before writing to csv, we force everything to ASCII,
    ignoring characters that don't play well.
    '''
    html = html.lower()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    NA = 'NA'
    scripts = soup.findAll("script")
    script = str(scripts[10])
    script_pos = script.find("profilepromo.params")
    if not (script_pos):
        print 'Profile likely deleted. Missing expected html structure.'
        return None, None

    script_pos = script.find("{",script_pos)
    script_end = script.find("};",script_pos)
    completeJson = script[script_pos:script_end] + "}"
    try:
        newDictionary = json.loads(completeJson)
    except ValueError:
        return {}, []
    profile = {}
    essay = {}
    essays = []
    language = {}
    languages = []
    photo = {}
    photos = []
    lookingFor = {}
    lookingFors = []
    ethnicity = {}
    ethnicities = []
    profile['username'] = newDictionary['jsparams']['username']
    profile['educationModifier'] = newDictionary['user']['details']['api_values']['education']['modifier']
    profile['educationValue'] = newDictionary['user']['details']['api_values']['education']['value']
    profile['childrenHave'] = newDictionary['user']['details']['api_values']['children']['have']
    profile['childrenWant'] = newDictionary['user']['details']['api_values']['children']['want']
    profile['monogamous'] = newDictionary['user']['details']['api_values']['monogamous']
    profile['drinking'] = newDictionary['user']['details']['api_values']['drinking']
    profile['gender'] = newDictionary['user']['details']['api_values']['gender']
    profile['cats'] = newDictionary['user']['details']['api_values']['pets']['cats']
    profile['dogs'] = newDictionary['user']['details']['api_values']['pets']['dogs']
    profile['weed'] = newDictionary['user']['details']['api_values']['weed']
    profile['birthDateYear'] = str(newDictionary['user']['details']['api_values']['birthdate']['year'])
    profile['birthDateMonth'] = str(newDictionary['user']['details']['api_values']['birthdate']['month'])
    profile['birthDateDay'] = str(newDictionary['user']['details']['api_values']['birthdate']['day'])
    profile['smoking'] = newDictionary['user']['details']['api_values']['smoking']
    profile['bodytype'] = newDictionary['user']['details']['api_values']['bodytype']
    profile['orientation'] = newDictionary['user']['details']['api_values']['orientation']
    profile['heightCm'] = str(newDictionary['user']['details']['api_values']['height']/100)
    profile['drugs'] = newDictionary['user']['details']['api_values']['drugs']
    profile['sign'] = newDictionary['user']['details']['api_values']['sign']
    profile['religionModifier'] = newDictionary['user']['details']['api_values']['religion']['modifier']
    profile['religionValue'] = newDictionary['user']['details']['api_values']['religion']['value']
    profile['diet'] = newDictionary['user']['details']['api_values']['diet']
    profile['locationCountryCode'] = newDictionary['user']['location']['country_code']
    profile['locationFormatted'] = newDictionary['user']['location']['formatted']['standard']
    profile['status'] = newDictionary['user']['details']['api_values']['status']

    x = newDictionary['user']['essays']
    for i in x:
        essay['rawContent'] = i['raw_content']
        essay['id'] = str(i['id'])
        essay['title'] = i['title']
        essay['username']=profile['username']
        essays.append(copy.deepcopy(essay))

    x = newDictionary['user']['details']['api_values']['languages']
    for i in x:
        language['fluency'] = i['fluency']
        language['language'] = i['language']
        language['username']=profile['username']
        languages.append(copy.deepcopy(language))

    x = newDictionary['user']['thumbs']
    for i in x:
        if i['info']['path'] is not None:
            photo['path'] = 'https://k3.okccdn.com/php/load_okc_image.php/images/' + i['info']['path']
            photo['username']=profile['username']
            photos.append(copy.deepcopy(photo))

    x = newDictionary['user']['details']['api_values']['lookingfor']
    count = 0
    for i in x:
        lookingFor['lookingFor'] = i
        lookingFor['id'] = str(count)
        lookingFor['username']=profile['username']
        lookingFor['metric']='Relationship'
        count += 1
        lookingFors.append(copy.deepcopy(lookingFor))

    x = newDictionary['user']['wiw']['pieces']
    for i in x:
        if i.find(u"age") == 0:
            firstNumStart = i.find(' ')+1
            firstNumEnd = firstNumStart+2
            secondNumStart = firstNumEnd + 1
            secondNumEnd = len(i)
            lookingFor['lookingFor'] = i[firstNumStart:firstNumEnd]
            lookingFor['id'] = str(count)
            lookingFor['username']=profile['username']
            lookingFor['metric'] = 'min_age'
            lookingFors.append(copy.deepcopy(lookingFor))
            count += 1
            lookingFor['lookingFor'] = i[secondNumStart:secondNumEnd]
            lookingFor['id'] = str(count)
            lookingFor['metric'] = 'max_age'
            lookingFors.append(copy.deepcopy(lookingFor))

    x = newDictionary['user']['details']['api_values']['ethnicity']
    count = 0
    for i in x:
        ethnicity['ethnicity'] = i
        ethnicity['id'] = str(count)
        ethnicity['username']=profile['username']
        count += 1
        ethnicities.append(copy.deepcopy(ethnicity))

    userExtraInfo = [essays, languages, photos, lookingFors, ethnicities]
    return profile, userExtraInfo


TIMING_MSG = '''%(elapsed)ds elapsed, %(completed)d profiles fetched, \
%(skipped)d skipped, \
%(remaining)d left, %(secs_per_prof).1fs per profile, \
%(prof_per_hour).0f profiles per hour, \
%(est_hours_left).1f hours left'''


def compute_elapsed_seconds(elapsed):
    '''Given a timedelta, returns a float of total seconds elapsed.'''
    return (elapsed.days * 60 * 60 * 24 +
            elapsed.seconds + elapsed.microseconds / 1.0e6)


def read_usernames(filename):
    '''Extracts usernames from the given file, returning a sorted list.

    The file should either be:
        1) A list of usernames, one per line
        2) A CSV file with a 'username' column (specified in its header line)
    '''
    try:
        rows = [r for r in csv.reader(open(filename))]
        try:
            idx = rows[0].index('username')
            unames = [row[idx].lower() for row in rows[1:]]
        except ValueError:
            unames = [r[0] for r in rows]
        return sorted(set(unames))
    except IOError, e:
        # File doesn't exist
        return []


def prepare_flags(argv):
    '''Set up flags. Returns true if the flag settings are acceptable.'''
    try:
        argv = FLAGS(argv)  # parse flags
    except gflags.FlagsError, e:
        return False
    return FLAGS.session_cookie and FLAGS.usernames_file and FLAGS.outfile


def main(argv):
    if not prepare_flags(argv):
        print 'Usage: %s ARGS\\n%s' % (sys.argv[0], FLAGS)
        sys.exit(1)

    usernames_to_fetch = read_usernames(FLAGS.usernames_file)
    if not usernames_to_fetch:
        print 'Failed to load usernames from %s' % FLAGS.usernames_file
        sys.exit(1)
    print 'Read %d usernames to fetch' % len(usernames_to_fetch)

    completed = read_usernames(FLAGS.completed_usernames_file)
    if completed:
        usernames_to_fetch = sorted(set(usernames_to_fetch) - set(completed))
        print '%d usernames were already fetched, leaving %d to do' % (
            len(completed), len(usernames_to_fetch))

    start = datetime.datetime.now()
    last = start
    headers_written = bool(completed)  # Only write headers if file is empty
    skipped = 0
    profile_writer = csv.writer(open(FLAGS.outfile, 'ab'))
    profile_writer2 = csv.writer(open(FLAGS.outfile2, 'ab'))
    profile_writer3 = csv.writer(open(FLAGS.outfile3, 'ab'))
    profile_writer4 = csv.writer(open(FLAGS.outfile4, 'ab'))
    profile_writer5 = csv.writer(open(FLAGS.outfile5, 'ab'))
    profile_writer6 = csv.writer(open(FLAGS.outfile6, 'ab'))
    completed_usernames_writer = open(FLAGS.completed_usernames_file, 'ab')
    N = len(usernames_to_fetch)
    # Fetch profiles
    for i, username in enumerate(usernames_to_fetch):
        # ** Critical ** so OKC servers don't notice and throttle us
        if i > 0:
            print "Sleeping..."
            # elapsed = datetime.datetime.now() - last
            # elapsed_sec = elapsed.seconds * 1.0 + elapsed.microseconds / 1.0e6
            # time.sleep(max(0, SLEEP_BETWEEN_QUERIES - elapsed_sec))
            time.sleep(SLEEP_BETWEEN_QUERIES)
        # Go ahead
        last = datetime.datetime.now()
        userExtraInfo = []
        profile, userExtraInfo = pull_profile_and_essays(username)
        if not profile:
            skipped += 1
        else:
            if not headers_written:
                header_row = list(sorted(profile))
                profile_writer.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
            row = tuple([profile[k] for k in sorted(profile)])
            row = [field.encode('ascii', 'ignore') for field in row]
            print row
            profile_writer.writerow(row)

            if not headers_written and len(userExtraInfo[0])>1:
                header_row = list(sorted(userExtraInfo[0][0]))
                profile_writer2.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
            for essayRow in userExtraInfo[0]:
                row = tuple(essayRow[k] for k in sorted(essayRow))
                row = [field.encode('ascii', 'ignore') for field in row]
                profile_writer2.writerow(row)

            if not headers_written and len(userExtraInfo[1])>1:
                header_row = list(sorted(userExtraInfo[1][0]))
                profile_writer3.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
            for essayRow in userExtraInfo[1]:
                row = tuple(essayRow[k] for k in sorted(essayRow))
                row = [field.encode('ascii', 'ignore') for field in row]
                profile_writer3.writerow(row)

            if not headers_written and len(userExtraInfo[2])>1:
                header_row = list(sorted(userExtraInfo[2][0]))
                profile_writer4.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
            for essayRow in userExtraInfo[2]:
                row = tuple(essayRow[k] for k in sorted(essayRow))
                row = [field.encode('ascii', 'ignore') for field in row]
                profile_writer4.writerow(row)

            if not headers_written and len(userExtraInfo[3])>1:
                header_row = list(sorted(userExtraInfo[3][0]))
                profile_writer5.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
            for essayRow in userExtraInfo[3]:
                row = tuple(essayRow[k] for k in sorted(essayRow))
                row = [field.encode('ascii', 'ignore') for field in row]
                profile_writer5.writerow(row)

            if not headers_written and len(userExtraInfo[4])>1:
                header_row = list(sorted(userExtraInfo[4][0]))
                profile_writer6.writerow(
                    [x.encode('ascii', 'ignore') for x in header_row])
                headers_written = True
            for essayRow in userExtraInfo[4]:
                row = tuple(essayRow[k] for k in sorted(essayRow))
                row = [field.encode('ascii', 'ignore') for field in row]
                profile_writer6.writerow(row)
            headers_written = True

        print >>completed_usernames_writer, username
        completed_usernames_writer.flush()
        if i % 10 == 0:
            elapsed = datetime.datetime.now() - start
            secs = compute_elapsed_seconds(elapsed)
            profiles_per_hour = (i+1.0)*3600/secs
            print '\n' + TIMING_MSG % {
                'elapsed': secs,
                'completed': i + 1,
                'skipped': skipped,
                'remaining': N - i - 1,
                'secs_per_prof': secs/(i+1.0),
                'prof_per_hour': profiles_per_hour,
                'est_hours_left': (N - i)/profiles_per_hour,
            }




if __name__ == '__main__':
        main(sys.argv)


