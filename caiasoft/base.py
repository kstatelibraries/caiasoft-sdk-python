import re
import os
import requests

class APIError(ValueError):
    pass

class Caiasoft(object):

    def __init__(self, api_key, site_name):
        self.api_key = api_key
        self.site_name = site_name

    @property
    def headers(self):
        """The HTTP headers needed for authenticated requests"""
        return {
            "X-API-Key": self.api_key,
        }

    def _request(self, endpoint: str, method='GET', params=None, data=None, json=None):
        
        """Make an authenticated request to the API, raise any API errors, and
        returns data.
        :param str endpoint: API URL
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        """

        api_url = f"https://{self.site_name}.caiasoft.com/api/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=api_url, params=params, json=json, data=data, headers=self.headers, timeout=30)

        if not response.json()['success']:
            raise APIError(f"Request to {response.url} returned {response.json()['error']}")

        if response.status_code != 200:
            print(response.json())
            raise APIError('Request to {} returned {}'.format(response.url, response.status_code))

        response = response.json()

        error_text = response['error']
        if error_text:
            raise APIError(error_text)

        return response

    def accessioned_items(self, accfrom: int, accto:int , collection: str = 'ALL') -> dict:
        """
        Get Accessioned Item List
        This returns all items, both accessioned (active) and deaccessioned
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """
        resp = self._request(f"/accessionedlist/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def accession_items_active(self, accfrom: int, accto:int , collection: str = 'ALL') -> dict:
        """
        Get Accessioned Item List of Active Items
        This returns only acessioned (active) items.
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        print(f"/accessioned_active/v1/{accfrom}/{accto}/{collection}")
        resp = self._request(f"/accessioned_active/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def accession_info(self, accfrom: int, accto: int, collection: str = 'ALL') -> dict:
        """
        Accessioned Item info - Use this API to receive back full info on accessioned items, not just a barcode list
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """
        resp = self._request(f"/accessioninfo/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'items': resp['items']})

    def missing_bibfield(self, bibfield: str, collection : str = 'ALL') -> dict:
        """
        Accessioned Item info - Use this API to receive back full info on accessioned items, not just a barcode list
        :param str bibfield: The following fields are accepted: none, title, author, callnumber, itemid.
            Use this parameter for a list of barcodes that are missing the bibfield info.
            Example: “title” will return all items that have no title in their bibliographic info.
            Note that “all” will return items with no bibliographic records or all of the accepted fields blank.
            Note that "none" means there is no additional information other than a barcode.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        valid_bibfields = ['none', 'title', 'author', 'callnumber', 'itemid', 'all']

        if bibfield.lower() not in valid_bibfields:
            raise APIError(f"{bibfield} is not a valid value for bibfield.")

        resp = self._request(f"bibmissing/v1/{collection}/{bibfield.lower()}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def circulation_request(self, barcode: str, request_type: str, stop: str,
        request_id: str = None, requestor: str = None, patron_id: str = None,
        title: str = None, author: str = None, volume: str = None,
        call_number: str = None, article_title: str = None, article_author: str = None,
        article_pages: str = None, details: str = None
    ) -> dict:
        """
        Circulation Requests

        :param str barcode: Alphanumeric String
        :param str request_type: Only values accepted: PYR, ERT, DEA, SHP
            Type of retrieval request which must match the job type requested,
            PYR (Physical Retrieval), ERT (E-Retrieval), DEA (Deaccession), SHP (SH-I-P service)
        :param str stop: Must match a stop name or code or stop location name or code from your circulation stops list
        :param str request_id: Unique Request identifier from the sending system.
            Note that duplicate entries with the same request ID will be skipped in processing
        :param str requestor: Name of requesting party
        :param str patron_id: ID or email of requesting party
        :param str title: Title of requested item
        :param str author: Author of requested item
        :param str volume: Volume of requested item
        :param str call_number: Call number of requested item
        :param str article_title: Article title of requested item (for use in ERT scanning)
        :param str article_author: Article author of requested item (for use in ERT scanning)
        :param str article_pages: Article pages of requested item (for use in ERT scanning)
        :param str details: Additional request details
        """
        valid_request_type = ['PYR', 'ERT', 'DEA', 'SHP']


        if request_type.upper() not in valid_request_type:
            raise APIError(f"{request_type} is not a valid value for request_type.")

        payload = [{
            "barcode": barcode,
            "request_type": request_type,
            "stop": stop,
            "request_id": request_id,
            "requestor": requestor,
            "patron_id": patron_id,
            "title": title,
            "author": author,
            "volume": volume,
            "call_number": call_number,
            "article_title": article_title,
            "article_author": article_author,
            "article_pages": article_pages,
            "details": details
        }]

        resp = self._request(f"circrequests/v1", method="POST", json={"requests": payload})
        return dict({"count": resp['request_count'], 'results': resp['results']})

    def item_info(self, barcode : str) -> dict:
        """
        Retreives Item Information
        :param str barcode: Alphanumeric String
        """
        resp = self._request(f"/item/v1/{barcode}")
        return dict({"count": len(resp['items']), 'items': resp['items']})

    def item_loc(self, barcode : str) -> dict:
        """
        Retreives Item Location
        :param str barcode: Alphanumeric String
        """
        resp = self._request(f"/itemloc/v1/{barcode}")
        return dict({"count": len(resp['item']), 'item': resp['item']})

    def items_by_barcode(self, barcodes : list) -> dict:
        """
        Items by Barcode - JSON sent to URL to find item status and info on one or more items in a single post
        :param list barcode: Alphanumeric String
        """
        resp = self._request("/itemsbybarcode/v1", method="POST", json={"barcodes": barcodes})
        return dict({"count": resp['item_count'], 'items': resp['items']})

    def item_location_by_barcode(self, barcodes : list) -> dict:
        """
        Item Location List
        :param list barcode: Alphanumeric String
        """
        resp = self._request("/itemloclist/v1", method="POST", json={"items": barcodes})
        return dict({"count": len(resp['item']), 'items': resp['item']})
