#!/usr/bin/env python

import agate


def make_countries_json():
    eu_countries_parliament = agate.Table.from_csv('output/eu_countries_parliament.csv')
    eu_countries_ep = agate.Table.from_csv('output/eu_countries_ep.csv')

    simple_parliament = eu_countries_parliament.select(['country', 'year', 'mean']).rename({ 'mean': 'parliament_mean' })
    simple_ep = eu_countries_ep.select(['country', 'year', 'mean']).rename({ 'mean': 'ep_mean' })

    simple_both = simple_parliament.join(simple_ep, ['country', 'year'])

    grouped = simple_both.group_by('country').exclude('country')

    grouped.to_json('src/data/countries.json', nested=True)


def make_all_json():
    eu_wide_parliament = agate.Table.from_csv('output/eu_wide_parliament.csv')
    eu_wide_ep = agate.Table.from_csv('output/eu_wide_ep.csv')

    simple_parliament = eu_wide_parliament.select(['year', 'mean']).rename({ 'mean': 'parliament_mean' })
    simple_ep = eu_wide_ep.select(['year', 'mean']).rename({ 'mean': 'ep_mean' })

    simple_both = simple_parliament.join(simple_ep, 'year')

    simple_both.to_json('src/data/eu.json')


if __name__ == '__main__':
    # make_countries_json()
    make_all_json()
