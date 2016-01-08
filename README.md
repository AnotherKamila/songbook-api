# songbook-api

This is the backend/API for my songbook -- see [the frontend's README](https://github.com/AnotherKamila/songbook-web) for more info.

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
