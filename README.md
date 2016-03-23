eu-polarization
===============

Analysis of political polarization using the [ParlGov database](http://www.parlgov.org/).

Setup
-----

Requires Python 3.

```
curl http://www.parlgov.org/static/stable/2015/parlgov-stable.db > data/parlgov-stable.db

mkvirtualenv eu-polarization
pip install -r requirements.txt
```

Run
---

```
python parl.py
```
