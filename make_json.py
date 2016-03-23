#!/usr/bin/env python

import agate


def main():
    eu_countries_parliament = agate.Table.from_csv('output/eu_countries_parliament.csv')
    eu_countries_ep = agate.Table.from_csv('output/eu_countries_ep.csv')

    simple_parliament = eu_countries_parliament.select(['country', 'year', 'mean']).rename({ 'mean': 'parliament_mean' })
    simple_ep = eu_countries_ep.select(['country', 'year', 'mean']).rename({ 'mean': 'ep_mean' })

    simple_both = simple_parliament.join(simple_ep, ['country', 'year'])

    grouped = simple_both.group_by('country').exclude('country')

    grouped.to_json('src/data/countries.json', nested=True)


if __name__ == '__main__':
    main()
