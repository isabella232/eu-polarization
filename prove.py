#!/usr/bin/env python

import agate
import proof


OECD = [
    'Australia',
    'Austria',
    'Belgium',
    'Canada',
    'Chile',
    'Czech Rep.',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Iceland',
    'Ireland',
    'Israel',
    'Italy',
    'Japan',
    'Korea',
    'Luxembourg',
    'Mexico',
    'Netherlands',
    'New Zealand',
    'Norway',
    'Poland',
    'Portugal',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'Switzerland',
    'Turkey',
    'UK',
    'USA'
]
NULL_VALUES = ['', '-999']

boolean = agate.Boolean(null_values=NULL_VALUES)
number = agate.Number(null_values=NULL_VALUES)
text = agate.Text(null_values=NULL_VALUES)


def load_data(data):
    tester = agate.TypeTester(types=[
        boolean,
        number,
        text
    ])

    data['dpi'] = agate.Table.from_csv('DPI2015_basefile.v5.csv', column_types=tester)


def add_value(data):
    key = {
        0: 'no data',
        1: 'right',
        2: 'center',
        3: 'left',
        None: 'no executive'
    }

    data['value_added'] = data['dpi'].compute([
        ('alignment', agate.Formula(text, lambda r: key[r['execrlc']])),
        ('any_nationalist', agate.Formula(boolean, lambda r: r['gov1nat'] or r['gov2nat'] or r['gov3nat'] or r['opp1nat'])),
        ('any_regionalist', agate.Formula(boolean, lambda r: bool(r['gov1reg'] or r['gov2reg'] or r['gov3reg'] or r['opp1reg'])))
    ])


def filter_oecd(data):
    data['oecd'] = data['value_added'].where(lambda r: r['countryname'] in OECD)


def by_alignment(data):
    pivot = data['oecd'].pivot('year', 'alignment')

    pivot.to_csv('by_alignment.csv')


def by_nationalism(data):
    pivot = data['oecd'].pivot('year', 'any_nationalist')

    pivot.to_csv('by_nationalism.csv')


def by_regionalism(data):
    pivot = data['oecd'].pivot('year', 'any_regionalist')

    pivot.to_csv('by_regionalism.csv')


def by_index(data):
    groups = data['oecd'].group_by('year')
    indices = groups.aggregate([
        ('average_herftot', agate.Mean('herftot'))
    ])

    indices.to_csv('by_index.csv')


if __name__ == '__main__':
    data_loaded = proof.Analysis(load_data)
    value_added = data_loaded.then(add_value)
    oecd_filtered = value_added.then(filter_oecd)
    oecd_filtered.then(by_alignment)
    oecd_filtered.then(by_nationalism)
    oecd_filtered.then(by_regionalism)
    oecd_filtered.then(by_index)

    data_loaded.run()
