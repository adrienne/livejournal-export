#!/usr/bin/python3

import json
import os
import requests
import xml.etree.ElementTree as ET
import auth


YEARS = range(1989, 2018)  # first to (last + 1)


def fetch_month_posts(year, month):
    response = requests.post(
        'http://www.livejournal.com/export_do.bml',
        headers=auth.get_headers(),
        cookies=auth.get_cookies(),
        data={
            'what': 'journal',
            'year': year,
            'month': '{0:02d}'.format(month),
            'format': 'xml',
            'header': 'on',
            'encid': '2',
            'field_itemid': 'on',
            'field_eventtime': 'on',
            'field_logtime': 'on',
            'field_subject': 'on',
            'field_event': 'on',
            'field_security': 'on',
            'field_allowmask': 'on',
            'field_currents': 'on'
        }
    )

    return response.text


def xml_to_json(xml):
    def f(field):
        return xml.find(field).text

    return {
        'id': f('itemid'),
        'date': f('logtime'),
        'subject': f('subject') or '',
        'body': f('event'),
        'eventtime': f('eventtime'),
        'security': f('security'),
        'allowmask': f('allowmask'),
        'current_music': f('current_music'),
        'current_mood': f('current_mood')
    }


def download_posts():
    os.makedirs('posts-xml', exist_ok=True)
    os.makedirs('posts-json', exist_ok=True)

    xml_posts = []
    for year in YEARS:
        for month in range(1, 13):
            print("Fetching for " + str(month) + ", " + str(year))
            xml = fetch_month_posts(year, month)
            xml_posts.extend(list(ET.fromstring(xml).iter('entry')))

            with open('posts-xml/{0}-{1:02d}.xml'.format(year, month), 'w+') as file:
                file.write(xml)

    json_posts = list(map(xml_to_json, xml_posts))
    with open('posts-json/all.json', 'w') as f:
        f.write(json.dumps(json_posts, ensure_ascii=False, indent=2))

    return json_posts


if __name__ == '__main__':
    download_posts()
