Database organization
=====================

Stuff is stored in [Redis](http://redis.io/). See [Redis Data Types](http://redis.io/topics/data-types-intro).

Conventions in this document
----------------------------

- `key => value` means `value` is stored at `key` in Redis
- data types: if not explicitly specified…
  - `foo`: string (in the suggested format)
  - `[ bar ]`: list
  - `{ baz }`: set
  - `M{ quux: flob }`: hash map ("Python dict")
  - `foo|bar`: type/format foo *or* type/format bar

Concepts, notes
---------------

Songbooks and songs are versioned, and old versions are not allowed to change. (Note: use SETNX and such.) For every songbook/song there is also a pointer to the latest version (I will call this "alias"), and usually stuff uses that alias to refer to "whatever the newest version is" instead of refering to a specific version.

This is to protect data without requiring a login: "updating" things in fact means just adding a new version (not touching the old ones) and pointing the versionless alias to the newer version. This alias overwrite is therefore the only destructive operation (and therefore the only action that requires some kind of authentication).

--------------------------------------------------------------------------------

IDs may or may not be meaningful -- any string valid as part of a URL is good. (Meaningful+pretty is encouraged, but up to the users.)

Data types
----------

### Book (Songbook)

`book:<id>:v<version> => { book:<id>|song:<id> }` -- a book may contain other books

The newest version is aliased by `book:<id>` => `book:<id>:v<newest-version>`

`book:<id>:unlisted => <whatever>` -- if key exists, this songbook will not be listed in the songbook index

### Song

`song:<id>:v<version> => M{ text: <text>, title: <title>, author: <author>, … }` -- all song metadata, used for the search index; and raw song text (as submitted -- not parsed)

The newest version is aliased by `song:<id>` => `song:<id>:v<newest-version>`

`song:<id>:unlisted => <whatever>` -- if key exists, this song will not be listed in the default songbook

### Authentication keys

`key:song:<id>|key:book:<id> => ugly_random_string`: key needed to update that alias (the user must supply this in update requests, otherwise unauthorized)

Note about usage: when creating something, this key will be generated and stored in the user's browser, and may be e.g. emailed to them (or they can just ask me for it :D)

--------------------------------------------------------------------------------

Note/TODO: Keeping old versions means there will be a lot of old versions. GC'ing unused stuff might be a good idea, but problem: what is "unused"? -- will worry about this when I run out of space :D
