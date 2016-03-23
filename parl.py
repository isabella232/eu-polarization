#!/usr/bin/env python

import statistics

from agate import csv
import sqlite3 as sqlite

EU = [
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Netherlands',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'United Kingdom'
]

ELECTION_TYPES = [
    'parliament',
    'ep'
]

EU_ELECTIONS_YEARS = [
    1979, 1984, 1989, 1994, 1999, 2004, 2009, 2014
]


def eu_wide(db, election_type):
    """
    Aggregate data for EU parliamentary elections.
    """
    summary_rows = []
    detail_rows = []

    for year in range(1980, 2016):
        left_right_list = []
        total_seats = 0

        print(year)

        for country in EU:
            results = db.execute('''
                SELECT DISTINCT election_date
                FROM view_election
                WHERE country_name=? AND CAST(SUBSTR(election_date, 0, 5) AS INTEGER) < ? AND election_type=?
                ORDER BY election_date DESC
                ''',
                (country, year, election_type)
            )

            try:
                election_date = results.fetchone()[0]
            except TypeError:
                continue

            print(country, election_date)

            results = db.execute('''
                SELECT party_name_english, seats, left_right
                FROM view_election
                WHERE country_name=? AND election_date=? AND election_type=?
                ''',
                (country, election_date, election_type)
            )

            for row in results:
                party_name, seats, left_right = row

                if not seats:
                    continue

                total_seats += seats

                if not left_right:
                    continue

                left_right_list.extend([left_right] * seats)

                for i in range(seats):
                    detail_rows.append([year, country, party_name, left_right])

        seats_with_score = len(left_right_list)
        mean_score = statistics.mean(left_right_list)
        median_score = statistics.median(left_right_list)
        stdev_score = statistics.stdev(left_right_list)

        summary_rows.append([year, seats_with_score, total_seats, mean_score, median_score, stdev_score])

    with open('output/eu_wide_%s.csv' % election_type, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['year', 'seats_with_score', 'total_seats', 'mean', 'median', 'stdev'])
        writer.writerows(summary_rows)

    with open('output/eu_details_%s.csv' % election_type, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['year', 'country', 'party_name', 'left_right'])
        writer.writerows(detail_rows)


def eu_countries(db, election_type):
    """
    Aggregate data for individual EU member-country national parliaments.
    """
    out_rows = []

    for country in EU:
        print(country)

        for year in range(1980, 2016):
            results = db.execute('''
                SELECT DISTINCT election_date
                FROM view_election
                WHERE country_name=? AND CAST(SUBSTR(election_date, 0, 5) AS INTEGER) < ? AND election_type=?
                ORDER BY election_date DESC
                ''',
                (country, year, election_type)
            )

            try:
                election_date = results.fetchone()[0]
            except TypeError:
                continue

            results = db.execute('''
                SELECT party_name_english, seats, seats_total, left_right
                FROM view_election
                WHERE country_name=? AND election_date=? AND election_type=?
                ''',
                (country, election_date, election_type)
            )

            left_right_list = []

            for row in results:
                name, seats, seats_total, left_right = row

                if not seats:
                    continue

                if not left_right:
                    continue

                left_right_list.extend([left_right] * seats)

            seats_with_score = len(left_right_list)
            mean_score = statistics.mean(left_right_list)
            median_score = statistics.median(left_right_list)
            stdev_score = statistics.stdev(left_right_list)

            out_rows.append([country, year, seats_with_score, seats_total, mean_score, median_score, stdev_score])

    with open('output/eu_countries_%s.csv' % election_type, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['country', 'year', 'seats_with_score', 'seats_total', 'mean', 'median', 'stdev'])
        writer.writerows(out_rows)


def main():
    db = sqlite.connect('data/parlgov-stable.db')

    # eu_wide(db, 'parliament')
    # eu_wide(db, 'ep')
    # eu_countries(db, 'parliament')
    eu_countries(db, 'ep')

if __name__ == '__main__':
    main()
