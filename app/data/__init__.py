import requests
from requests.exceptions import HTTPError

import logging


STEIN_BASE_URL = "https://api.steinhq.com/v1/storages/"

class Provider():

    _api_id = ''
    _api_password = ''
    _user_name = 'api_user'

    def __init__(self, config):
        self._api_id = config.get('STEIN_API_ID')
        self._api_password = config.get('STEIN_API_PASSWORD')
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
            "statuses": {},
            "stages": {}
        }
        for item in backlog:
            if item['status'] in metadata['statuses']:
                metadata['statuses'][item['status']] += 1
            else:
                metadata['statuses'][item['status']] = 1
            if item['stage'] in metadata['stages']:
                metadata['stages'][item['stage']] += 1
            else:
                metadata['stages'][item['stage']] = 1
        return metadata


    def fetch_backlog(self):
        backlog_url = self.build_url('backlog')
        items, error, status = self.fetch_url(backlog_url)
        logging.warn(items)
        if status:
            cleaned_backlog = []
            for item in items:
                current_item = self.clean_item(item)
                cleaned_backlog.append(current_item)
            return {
                    'records': cleaned_backlog,
                    'metadata': self.build_metadata(cleaned_backlog)
            }, error, status
        else:
            return items, error, status


DefaultProvider = SteinProvider
