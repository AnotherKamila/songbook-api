# songbook-api

This is the backend/API for my songbook -- see [the frontend's README](https://github.com/AnotherKamila/songbook-web) for more info.

[![Heroku status](https://heroku-badge.herokuapp.com/?app=spevnik47-api)](https://spevnik47-api.herokuapp.com/)
[![Requirements Status](https://requires.io/github/AnotherKamila/songbook-api/requirements.svg?branch=master)](https://requires.io/github/AnotherKamila/songbook-api/requirements/?branch=master)
[![Floobits Status](https://floobits.com/kamila/songbook.svg)](https://floobits.com/kamila/songbook/redirect)

Development Quick Start
-----------------------

Note: This is the API server. The web frontend is [AnotherKamila/songbook-web](https://github.com/AnotherKamila/songbook-web).

- requires Python 3.4
- first-time setup:
  1. create virtualenv: `pyvenv ./venv` (or `pyvenv-3.4 ./venv`)
  2. activate virtualenv:
     - bash, zsh: `source venv/bin/activate`
     - fish: `. venv/bin/activate.fish`
     - csh, tcsh: `source venv/bin/activate.csh`
  3. Install dependencies: `pip install -r requirements.txt`
- always do stuff inside the venv (don't forget to activate it)
- start server with `python ./server.py` (or `heroku local`)
  - automatically reloads when sources change
- requires the `REDISCLOUD_URL` environment variable to be set to your Redis URL
- read `database.md` for the data model and how stuff is stored
