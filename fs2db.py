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
import sys

import redis

from songbook.ref import Ref, refjoin, is_reflike
from songbook.db_conventions import PUBLIC_LIST, refjoin

##### filename manipulation #####

def name_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]

def normalized(path):
    TRANSLIT_FROM = ' àáäâæçčďèéëêěìíïîľĺňñòóöôŕřšßťùúüůûýž'
    TRANSLIT_TO   = '-aaaaeccdeeeeeiiiillnnoooorrsstuuuuuyz'

    lname = name_from_path(path).lower().strip()
    for ca, cb in zip(TRANSLIT_FROM, TRANSLIT_TO):
        lname = lname.replace(ca, cb)
    lname = lname.replace(r'[^a-zA-Z0-9_-\/]', '-')

    return lname

def songref(name):
    print(normalized(name))
    print(refjoin('song', normalized(name)))
    return refjoin('song', normalized(name))

def bookref(name):
    return refjoin('book', normalized(name))

##### database #####

# TODO support versioning :D
VERSION = 'v0'
def versioned(ref):
    return refjoin(ref, VERSION)

db_url = os.environ.get('REDIS_URL')
if not db_url: sys.exit('REDIS_URL not set, exiting.')
db = redis.from_url(db_url)

def add_book(path):
    name = name_from_path(path)
    ref = bookref(name)
    db.set(ref, VERSION)
    db.hmset(versioned(ref), {'title': name})

def add_song(filepath):
    # TODO metadata

    ref = songref(filepath)
    db.set(ref, VERSION)
    with open(filepath) as file:
        db.hmset(versioned(ref), {
            'title': name_from_path(filepath),
            'text':  file.read(),
        })

def add_ref_to_book(book, ref):
    db.sadd(refjoin(versioned(book), 'contents'), ref)

##### main #####

def stuff_into_redis(startdir):
    add_book(PUBLIC_LIST)
    for childdirname in os.listdir(startdir):
        childdir = os.path.join(startdir, childdirname)
        for dirpath, dirnames, filenames in os.walk(childdir, topdown=False, followlinks=True):

            print('{}:'.format(name_from_path(dirpath)))
            add_book(dirpath)

            for filename in filenames:
                path = os.path.join(dirpath, filename)
                print("    - song: {}".format(filename))
                add_song(path)
                add_ref_to_book(bookref(dirpath), songref(path))

            for dirname in dirnames:
                print("    * book: {}".format(dirname))
                add_ref_to_book(bookref(dirpath), bookref(dirname))

            add_ref_to_book(PUBLIC_LIST, bookref(dirpath))
            print()

def show_ref(ref, depth=0):
    ref = Ref.from_str(ref)
    assert ref.typename in ('book', 'song')
    vref = refjoin(ref, db.get(ref))
    if ref.typename == 'song':
        title = db.hget(vref, 'title').decode('utf-8')
        yield '{}song: {} ({})'.format(' '*2*depth, title, vref)
    else:
        title = db.hget(vref, 'title').decode('utf-8')
        yield '{}book: {} ({})'.format(' '*2*depth, title, vref)
        for child in db.smembers(refjoin(vref, 'contents')):
            for x in show_ref(child, depth+1): yield x

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <startdir>'.format(sys.argv[0]))
        sys.exit(47)
    stuff_into_redis(sys.argv[1])
    print('========= verification: public list: =========')
    for line in show_ref(PUBLIC_LIST): print(line)
