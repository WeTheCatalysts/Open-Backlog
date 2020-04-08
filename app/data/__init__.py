from flask import current_app

import requests
import datetime
from requests.exceptions import HTTPError

import logging
import constants


STEIN_BASE_URL = "https://api.steinhq.com/v1/storages/"


class CachedProvider():

    def fetch_from_cache(self, key):
        if key in current_app.config:
            logging.warn("HAS KEY")
            if current_app.config[key]:
                logging.warn("HAS DATA")
                cached_data =  current_app.config[key]
                logging.warn(cached_data)
                logging.warn("FROM CACHE")
                if cached_data['expires'] > datetime.datetime.now():
                    logging.warn("NOT EXPIRED")
                    return cached_data['records']
                else:
                    logging.warn("EXPIRED")
                    self.expire_from_cache(key)
                    return False
            else:
                return False
        else:
            return False

    def expire_from_cache(self, key):
        logging.warn("EXPIRE FROM CACHE")
        del current_app.config[key]


    def add_to_cache(self, key, object):
        logging.warn("ADD TO CACHE")
        cached_data = {
            "expires": datetime.datetime.now() + datetime.timedelta(seconds=constants.CACHE_EXPIRY),
            "records": object
        }
        logging.warn(cached_data)
        current_app.config[key] = cached_data

    def build_key(self, item_type, organisation, identifier):
        if identifier:
            key = item_type + "_" + organisation + "_" + identifier
        else:
            key  = item_type + "_" + organisation
        return key



class Provider():

    _api_id = ''
    _api_password = ''
    _user_name = 'api_user'

    def __init__(self, api_id, api_password):
        self._api_id = api_id
        self._api_password = api_password
    pass



class SteinProvider(Provider):

    def build_url(self, route):
        return f"https://api.steinhq.com/v1/storages/{self._api_id}/{route}"

    def fetch_url(self, url):
        content = {}
        error = None
        success = False
        response = None
        try:
            response = requests.get(url, auth=(self._user_name, self._api_password))
            response.raise_for_status()

        except HTTPError as http_err:
            content = None
            error = {
                "message": f'HTTP error occurred: {http_err}',
                "status": response.status_code
            }
        except Exception as err:
            if response is not None:
                error = {
                    "message": f'Other error occurred: {err}',
                    "status": response.status_code
                }
            else:
                error = {
                    "message": 'Unable to connect to datastore',
                    "status": 500
                }
        else:
            content = response.json()
            success = True
            error = None
        return content, error, success

    def clean_item(self, item):
        clean_item = {}
        for element in item:
            if '__' not in element:
                clean_item[element] = item[element]
        return clean_item


    def build_metadata(self, backlog):
        metadata = {
            "stats": {
                "statuses": {},
                "stages": {},
                "itemcount": 0
            }
        }
        itemcount = 0
        for item in backlog:
            itemcount += 1
            if item['status'] in metadata['stats']['statuses']:
                metadata['stats']['statuses'][item['status']] += 1
            else:
                metadata['stats']['statuses'][item['status']] = 1
            if item['stage'] in metadata['stats']['stages']:
                metadata['stats']['stages'][item['stage']] += 1
            else:
                metadata['stats']['stages'][item['stage']] = 1
        metadata['itemcount'] = itemcount
        return metadata


    def fetch_organisations(self):
        cached_data = CachedProvider().fetch_from_cache('organisations')
        if cached_data:
            return cached_data, None, True
        else:
            organisation_url = self.build_url('organisations')
            items, error, status = self.fetch_url(organisation_url)
            if status:
                organisation_count = 0
                cleaned_organisations = []
                for item in items:
                    if item["steinApiId"] is not None:
                        current_item = item
                        organisation_count += 1
                        cleaned_organisations.append(current_item)
                data_object = {
                        'metadata': {'organisation_count': organisation_count},
                        'datatype': 'organisations',
                        'records': cleaned_organisations,
                }
                CachedProvider().add_to_cache('organisations', data_object)

                return data_object, error, status
            else:
                return items, error, status



    def fetch_backlog(self):
        key = CachedProvider().build_key('backlog', self._api_id, None)
        cached_data = CachedProvider().fetch_from_cache(key)
        if cached_data:
            logging.warn(cached_data)
            return cached_data, None, True
        else:
            backlog_url = self.build_url('backlog')
            items, error, status = self.fetch_url(backlog_url)
            if status:
                cleaned_backlog = []
                for item in items:
                    current_item = self.clean_item(item)
                    if current_item['status'] not in ['hidden']:
                        if current_item['initiativeName'] is not None:
                            cleaned_backlog.append(current_item)
                data_object = {
                        'records': cleaned_backlog,
                        'metadata': self.build_metadata(cleaned_backlog),
                        'datatype': 'backlog',
                        'constants': {
                            'stages':constants.STAGES
                        }
                    }
                CachedProvider().add_to_cache(key, data_object)
                return data_object, error, status
            else:
                return items, error, status


    def fetch_backlog_item(self, itemId):
        logging.warn(itemId)
        backlog_url = self.build_url('backlog')
        items, error, status = self.fetch_url(backlog_url)
        if status:
            item_data = None
            for item in items:
                if item['itemId']:
                    if item['itemId'] == itemId:
                        item_data = self.clean_item(item)
            if item_data is not None:
                return {
                        'record': item_data,
                        'metadata': {},
                        'datatype': 'record'
                        } , error, status
            else:
                return None, {
                        "status": 404,
                        "message": "The specified item could not be found"
                    }, False
        else:
            return items, error, status


DefaultProvider = SteinProvider
