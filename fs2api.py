#!/usr/bin/env python3
"""
Stuffs a directory structure into Redis, in the format that the API expects.
Symlinks are followed.

The directory structure should look something like:
```
$ tree -l
.
├── české -> ../české/
│   ├── Ho ho Watanay.txt
│   ├── Strom.txt
│   ├── Tři kříže.txt
│   ├── Variace na renesanční téma.txt
│   └── Všech vandráků múza.txt
├── random -> ../random/
│   ├── Fear Not This Night.txt
│   └── Write in C.txt
├── test
│   └── dir
│       └── aa
└── Trojsten Originals -> ../Trojsten Originals/
    ├── Férum.txt
    ├── Fonos Kultivovaných Slečien.txt
    ├── Hymna iKS.txt
    ├── Mandarinka Majinka.txt
    ├── Medzi stenami.txt
    ├── Nepoznám.txt
    ├── O vládnej koalícii.txt
    ├── Pár vstupov.txt
    ├── Pieseň behu.txt
    ├── Riešte FKS.txt
    └── Syseľ bol chlap.txt

5 directories, 19 files
```
"""

import os
import re
import sys


import redis
import requests

# from songbook.ref import Ref, refjoin, is_reflike
# from songbook.db_conventions import PUBLIC_BOOKS_LIST, PUBLIC_SONGS_LIST, contents_ref

# ##### filename manipulation #####

# def name_from_path(path):
#     return os.path.splitext(os.path.basename(path))[0]

# # TODO normalized is not this-specific -- should be split from path manip and
# # put into db_conventions
# def normalized(path):
#     TRANSLIT_FROM = ' àáäâæçčďèéëêěìíïîľĺňñòóöôŕřšßťùúüůûýž'
#     TRANSLIT_TO   = '-aaaaeccdeeeeeiiiillnnoooorrsstuuuuuyz'

#     lname = name_from_path(path).lower().strip()
#     for ca, cb in zip(TRANSLIT_FROM, TRANSLIT_TO):
#         lname = lname.replace(ca, cb)
#     lname = re.sub(r'[\'"!?]', '', lname)
#     lname = re.sub(r'[^a-zA-Z0-9_\/]', '-', lname)

#     return lname

# def songref(name):
#     return refjoin('song', normalized(name))

# def bookref(name):
#     return refjoin('book', normalized(name))

# ##### parsing file contents #####
# # this is all temporary :D
# # right?! :D

# def parse_txt(text):
#     """My custom text+chords format."""
#     for pat in r'^#.*$', r'[\t ]+$':
#         text = re.sub(pat, '', text)
#     text = re.sub('\r?\n(\r?\n)+', '\n\n', text)
#     first_sec, rest = text.split('\n\n', 1)
#     data = {'text': text}
#     for line in first_sec.split('\n'):
#         meta_match = re.match(r'^(\w+)\s*:\s*(.*)$', line)
#         if not meta_match: return {'text': text}  # this is not a meta section
#         key, value = meta_match.group(1, 2)
#         data[normalized(key)] = value
#     return data

# def parse_abc(abc):
#     """Parses metadata from the ABC music notation."""
#     key_names = {
#         'C': 'artist',
#         'T': 'title',
#     }
#     data = {'abc': abc}
#     for line in abc.split('\n'):
#         for k in key_names:
#             if line.startswith(k+':'):
#                 v = line.split(':', 1)[1]
#                 data[key_names[k]] = v
#     return data

# parsers = {
#     '.txt': parse_txt,
#     '.abc': parse_abc,
# }

# ##### database #####

# # TODO support versioning :D
# VERSION = 'v0'
# def versioned(ref):
#     return refjoin(ref, VERSION)

# db_url = os.environ.get('REDIS_URL')
# if not db_url: sys.exit('REDIS_URL not set, exiting.')
# db = redis.from_url(db_url)

# def add_book(path):
#     name = name_from_path(path)
#     ref = bookref(name)
#     db.set(ref, VERSION)
#     db.hmset(versioned(ref), {'title': name})

# def add_song(filepath):
#     ext = os.path.splitext(filepath)[1]
#     if not ext in parsers:
#         print("W: No parser for {}, skipping {}".format(ext, filepath))
#         return None
#     ref = songref(filepath)
#     db.set(ref, VERSION)
#     with open(filepath) as file:
#         db.hmset(versioned(ref), parsers[ext](file.read()))
#     return ref

# def add_ref_to_book(book, ref):
#     db.sadd(contents_ref(versioned(book)), ref)

# ##### main #####

# def stuff_into_redis(startdir):
#     add_book(PUBLIC_BOOKS_LIST)
#     add_book(PUBLIC_SONGS_LIST)
#     for childdirname in os.listdir(startdir):
#         childdir = os.path.join(startdir, childdirname)
#         for dirpath, dirnames, filenames in os.walk(childdir, topdown=False, followlinks=True):

#             print('{}:'.format(name_from_path(dirpath)))
#             add_book(dirpath)
#             add_ref_to_book(PUBLIC_BOOKS_LIST, bookref(dirpath))

#             for filename in filenames:
#                 path = os.path.join(dirpath, filename)
#                 if add_song(path):
#                     print("    - song: {}".format(filename))
#                     add_ref_to_book(PUBLIC_SONGS_LIST, songref(path))
#                     add_ref_to_book(bookref(dirpath), songref(path))

#             for dirname in dirnames:
#                 print("    * book: {}".format(dirname))
#                 add_ref_to_book(bookref(dirpath), bookref(dirname))

#             print()

# def hgets(ref, key):
#     x = db.hget(ref, key)
#     return x.decode('utf-8') if x else None

# def show_ref(ref, depth=0):
#     ref = Ref.from_str(ref)
#     assert ref.typename in ('book', 'song')
#     vref = refjoin(ref, db.get(ref))
#     if ref.typename == 'song':
#         title =  hgets(vref, 'title')
#         artist = hgets(vref, 'artist')
#         yield '{}song: {} - {} ({})'.format(' '*2*depth, title, artist, vref)
#     else:
#         title  = hgets(vref, 'title')
#         yield '{}book: {} ({})'.format(' '*2*depth, title, vref)
#         for child in db.smembers(contents_ref(vref)):
#             for x in show_ref(child, depth+1): yield x

# if __name__ == '__main__':
#     if len(sys.argv) != 2:
#         print('Usage: {} <startdir>'.format(sys.argv[0]))
#         sys.exit(47)
#     stuff_into_redis(sys.argv[1])
#     print('========= verification: public list: =========')
#     for line in show_ref(PUBLIC_BOOKS_LIST): print(line)

API_URL = 'http://localhost:{}/'.format(os.environ.get('PORT', '5000'))

def check_status(r, good):
    if not r.status_code in good:
        print('ERROR: {} {} returned {} {}'.format(r.request.method, r.url, r.status_code, r.reason))
        sys.exit(1)

if __name__ == '__main__':
    user = {'type': 'passcode', 'id': 'importer', 'passcode': 'noprod'}
    user2 = {'type': 'passcode', 'id': 'importer', 'passcode': 'ble'}

    r = requests.post(API_URL+'/song/test', json={'user': user, 'data': {'key': 'value'}})
    check_status(r, [201])
    d = r.json()

    r = requests.put(API_URL+'/song/test', json={'user': user, 'version': d['version']})
    check_status(r, [200])

    r = requests.get(API_URL+'/song/test', allow_redirects=False)
    check_status(r, [301,302,303])
    if d['url'] != r.headers['Location']: raise ValueError('API behaving strangely')
