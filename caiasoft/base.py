"""
Basic library for intergrating with the Caiasoft API
"""
import re
from itertools import islice

import requests
from pydantic import BaseModel


class APIError(ValueError): # pylint: disable=missing-class-docstring,unnecessary-pass
    pass

class Caiasoft(): # pylint: disable=missing-class-docstring
    def __init__(self, api_key, site_name):
        self.api_key = api_key
        self.site_name = site_name
        self.timeout = 30
        self.valid_bibfields = ['none', 'title', 'author', 'callnumber', 'itemid', 'all']

    @property
    def headers(self):
        """The HTTP headers needed for authenticated requests"""
        return {
            "X-API-Key": self.api_key,
        }

    def set_timeout(self, timeout=30):
        """Set the HTTP Timeout"""
        self.timeout = timeout

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
        response = requests.request(
            method=method,
            url=api_url,
            params=params,
            json=json,
            data=data,
            headers=self.headers,
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise APIError(f"Request to {response.url} returned {response.status_code}")

        if not response.json()['success']:
            raise APIError(f"Request to {response.url} returned {response.json()['error']}")

        response = response.json()

        error_text = response['error']
        if error_text:
            raise APIError(error_text)

        return response

    def _validate_date(self, date: str) -> bool or str:
        """
        Validate the Datestamp
        :param str date: Date format YYYYMMDD
        """
        if not re.match(r"(19|20)(\d{2})(\d{2})(\d{2})", date):
            raise APIError('Date needs to be formatted as YYYYMMDD')
        return date

    def _split_data(self, data, size=500):
        data = iter(data)
        return iter(lambda: tuple(islice(data, size)), ())

    def accessioned_items(self, accfrom: str, accto:str , collection: str = 'ALL') -> dict:
        """
        Get Accessioned Item List
        This returns all items, both accessioned (active) and deaccessioned
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        resp = self._request(f"/accessionedlist/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def accession_items_active(self, accfrom: str, accto:str , collection: str = 'ALL') -> dict:
        """
        Get Accessioned Item List of Active Items
        This returns only acessioned (active) items.
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        resp = self._request(f"/accessioned_active/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def accession_info(self, accfrom: str, accto: str, collection: str = 'ALL') -> dict:
        """
        Accessioned Item info - Use this API to receive back full info on accessioned items, not just a barcode list
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        resp = self._request(f"/accessioninfo/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'items': resp['items']})

    def accession_info_active(self, accfrom: str, accto: str, collection: str = 'ALL') -> dict:
        """
        Accessioned Item info - Use this API to receive back full info on accessioned items currently active/ have not been de-accessioned.
        Additional info on items provided.
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        resp = self._request(f"/accessioninfo_active/v1/{accfrom}/{accto}/{collection}")
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

        if bibfield.lower() not in self.valid_bibfields:
            raise APIError(f"{bibfield} is not a valid value for bibfield.")

        resp = self._request(f"/bibmissing/v1/{collection}/{bibfield.lower()}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def missing_bibfield_bydate(self, accfrom: str, accto: str, bibfield: str, collection : str = 'ALL') -> dict:
        """
        Item Bibliographic Information Missing - Use this API to receive a list of items by date
            accesssed that do not have certain bibliographic details on file.
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str bibfield: The following fields are accepted: none, title, author, callnumber, itemid.
            Use this parameter for a list of barcodes that are missing the bibfield info for
                items accessed in the date parameters provided.
            Example: “title” will return all items that have no title in their bibliographic info.
            Note that “all” will return items with no bibliographic records or all of the accepted fields blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        if bibfield.lower() not in self.valid_bibfields:
            raise APIError(f"{bibfield} is not a valid value for bibfield.")

        resp = self._request(f"/bibmissing_bydate/v1/{accfrom}/{accto}/{collection}/{bibfield.lower()}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def deaccessioned_items(self, deafrom: str, deato:str , includereaccession: bool = False, collection: str = 'ALL') -> dict:
        """
        Get Accessioned Item List
        This returns all items, both accessioned (active) and deaccessioned
        :param str deafrom: date in YYYYMMDD format
        :param str deato: date in YYYYMMDD format, Repeat deafrom date for one day. Field cannot be blank.
        :param bool includereaccession: If True, Include items that have since been reaccessioned
        If False (default) Only list items that are still status DEA
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(deafrom)
        self._validate_date(deato)
        includereaccession = "Y" if includereaccession else "N"

        resp = self._request(f"/deaccessionedlist/v1/{deafrom}/{deato}/{collection}/{includereaccession}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def deaccession_info(self, deafrom: str, deato:str , includereaccession: bool = False, collection: str = 'ALL') -> dict:
        """
        Accessioned Item info - Use this API to receive back full info on accessioned items, not just a barcode list
        :param str deafrom: date in YYYYMMDD format
        :param str deato: date in YYYYMMDD format, Repeat deafrom date for one day. Field cannot be blank.
        :param bool includereaccession: If True, Include items that have since been reaccessioned
        If False (default) Only list items that are still status DEA
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(deafrom)
        self._validate_date(deato)
        includereaccession = "Y" if includereaccession else "N"

        resp = self._request(f"/deaccessioninfo/v1/{deafrom}/{deato}/{collection}/{includereaccession}")
        return dict({"count": resp['count'], 'items': resp['items']})

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

        resp = self._request("circrequests/v1", method="POST", json={"requests": payload})
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
        output = {
            "item_count": 0,
            "items": []
        }

        # We split the data into smaller pieces since there can be large data sets, and the server may timeout
        for small_chunk in self._split_data(barcodes, 500):
            resp = self._request("/itemsbybarcode/v1", method="POST", json={"barcodes": list(small_chunk)})
            output['item_count'] += int(resp['item_count'])
            output['items'] = output['items'] + resp['items']
        return dict({"count": output['item_count'], 'items': output['items']})

    def item_location_by_barcode(self, barcodes : list) -> dict:
        """
        Item Location List
        :param list barcode: Alphanumeric String
        """

        output = {
            "items": []
        }

        # We split the data into smaller pieces since there can be large data sets, and the server may timeout
        for small_chunk in self._split_data(barcodes, 500):
            resp = self._request("/itemloclist/v1", method="POST", json={"items": list(small_chunk)})
            output['items'] = output['items'] + resp['item']
        return dict({"count": len(output['items']), 'items': output['items']})


    def circ_stop_out(self, circstop="ALL") -> dict:
        """
        Circulation Stop - Items Outstanding
        :param bool active_only: Boolean Value. If True only return active stops.
            If False, show all active and inactive circulation stops
        """
        resp = self._request(f"/circstopout/v1/{circstop}", method="GET")
        items_out = []
        for item in resp['items_out']:
            circstop = item['circulation_stop'].split("-")
            item['circulation_stop_code'] = circstop[0].strip()
            item['circulation_stop_description'] = circstop[1].strip()
            items_out.append(item)

        return dict({"count": resp['count'], 'items_out': items_out})

    def circ_stop_list(self, active_only=True) -> dict:
        """
        Circulation Stop List
        :param bool active_only: Boolean Value. If True only return active stops.
            If False, show all active and inactive circulation stops
        """
        location = "ACTIVE" if active_only else "ALL"
        resp = self._request(f"/circstoplist/v1/{location}", method="GET")
        return dict({"count": resp['count'], 'stoplist': resp['stoplist']})

    def item_status(self, barcode : str) -> dict:
        """
        Retreives Item Status
        :param str barcode: Alphanumeric String
        """
        resp = self._request(f"/itemstatus/v1/{barcode}")
        item = [{
            "barcode": resp['barcode'],
            "status": resp['status']
        }]

        return dict({"count": len(item), 'item': item})

    def item_status_by_barcodes(self, barcodes : list) -> dict:
        """
        Item Status from List - JSON sent to URL to find item status and info on one or more items in a single post
        :param list barcode: Alphanumeric String
        """

        output = {
            "item_count": 0,
            "items": []
        }

        # We split the data into smaller pieces since there can be large data sets, and the server may timeout
        for small_chunk in self._split_data(barcodes, 500):
            resp = self._request("/itemstatuslist/v1/", method="POST", json={"barcodes": list(small_chunk)})
            output['item_count'] += int(resp['item_count'])
            output['items'] = output['items'] + resp['items']
        return dict({"count": output['item_count'], 'items': output['items']})

    def refiled_list(self, accfrom: str, accto: str, collection : str = 'ALL') -> dict:
        """
        Refiled Item List
        :param str accfrom: date in YYYYMMDD format
        :param str accto: date in YYYYMMDD format, Repeat accfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(accfrom)
        self._validate_date(accto)

        resp = self._request(f"refiledlist/v1/{accfrom}/{accto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def retrieval_info(self, retfrom: str, retto: str, collection : str = 'ALL') -> dict:
        """
        Retrieval Item info - Use this API to receive back full info on retrieved items, not just a barcode list
        :param str retfrom: date in YYYYMMDD format
        :param str retto: date in YYYYMMDD format, Repeat retfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(retfrom)
        self._validate_date(retto)

        resp = self._request(f"retrievalinfo/v1/{retfrom}/{retto}/{collection}")
        return dict({"count": resp['count'], 'items': resp['items']})

    def retrieved_list(self, retfrom: str, retto: str, collection : str = 'ALL') -> dict:
        """
        Retrieved Item List
        :param str retfrom: date in YYYYMMDD format
        :param str retto: date in YYYYMMDD format, Repeat retfrom date for one day. Field cannot be blank.
        :param str collection: alphanumeric string, Single collection or Report Class (group of collections) accepted.
            Use “ALL” for all collections.
        """

        self._validate_date(retfrom)
        self._validate_date(retto)

        resp = self._request(f"retrievedlist/v1/{retfrom}/{retto}/{collection}")
        return dict({"count": resp['count'], 'barcodes': resp['barcodes']})

    def item_updates(self, items: dict) -> dict:
        """
        Item Attribute Update - JSON sent to URL to process bibliographic information updates
            on one or more items in a single post
            Note: items will only be updated if information sent does not match info on file.
            Blank values will not be updated (empty title value will not overwrite existing title on file).
        :param items dict: This should be a dict with the following fields
            barcode (required), title, author, volume, call_number, collection,
            material, oclc, issn, isbn, edition, copy_number, pages, publisher,
            pub_place, pub_year, physical_desc, format, packaging, condition,
            shared_contrib, item_type, bib_location, bib_item_status,
            bib_item_code,bib_level, bib_item_id, bib_record_nbr

        Note: To update a field with a null value in order to clear the field, send the term "CLEARFIELD*" as the field value.
        """

        payload = []
        for item in items:
            payload.append(Item(**item).dict(exclude_none=True))

        output = {
            "total_count": 0,
            "updated_count": 0,
            "errors": [],
            "warnings": []
        }

        # We split the data into smaller pieces since there can be large data sets, and the server may timeout
        for small_chunk in self._split_data(payload, 500):
            resp = self._request("itemupdates/v1", method="POST", json={"items": small_chunk})
            output['total_count'] += int(resp['total_count'])
            output['updated_count'] += int(resp['updated_count'])
            output['errors'] = output['errors'] + resp['errors']
            output['warnings'] = output['warnings'] + resp['warnings']

        return output

    def incoming_items(self, items: dict) -> dict:
        """
        Incoming Accession Items - JSON sent to URL to process one or more incoming accession items in a single post
            Note: items will only be updated if information sent does not match info on file.
            Blank values will not be updated (empty title value will not overwrite existing title on file).
        :param items dict: This should be a dict with the following fields
            barcode (required), title, author, volume, call_number, collection,
            material, oclc, issn, isbn, edition, copy_number, pages, publisher,
            pub_place, pub_year, physical_desc, format, packaging, condition,
            shared_contrib, item_type, bib_location, bib_item_status,
            bib_item_code,bib_level, bib_item_id, bib_record_nbr

        Note: To update a field with a null value in order to clear the field, send the term "CLEARFIELD*" as the field value.
        """

        payload = []
        for item in items:
            payload.append(Item(**item).dict(exclude_none=True))

        output = {
            "incoming_count": 0,
            "rejected_count": 0,
            "rejects": [],
            "warnings": []
        }

        # We split the data into smaller pieces since there can be large data sets, and the server may timeout
        for small_chunk in self._split_data(payload, 500):
            resp = self._request("incomingitems/v1", method="POST", json={"incoming": small_chunk})
            output['incoming_count'] += int(resp['incoming_count'])
            output['rejected_count'] += int(resp['rejected_count'])
            output['rejects'] = output['rejects'] + resp['rejects']
            output['warnings'] = output['warnings'] + resp['warnings']

        return output

    def union_author(self, author : str, collection: str = None) -> dict:
        """
        Item Location List
        :param str author: Portion of title - to be searched for as a contains - string appears somewhere in the title
        :param str collection (Optional): Must match a collection code assigned to at least one active item
        """

        resp = self._request(f"/union_author/v1", method="POST", json={"author": author })
        return dict({"count": resp['item_count'], 'items': resp['items']})

    def union_callnumber(self, callnumber : str, collection: str = None) -> dict:
        """
        Item Location List
        :param str callnumber: Beginning of Call Number - string starts the Call Number
            Note: Normalized version of call number sent will also be searched
        :param str collection (Optional): Must match a collection code assigned to at least one active item
        """

        resp = self._request(f"/union_callnumber/v1", method="POST", json={"callnumber": callnumber })
        return dict({"count": resp['item_count'], 'items': resp['items']})

class Item(BaseModel): # pylint: disable=too-few-public-methods
    """
    :param barcode str: Item Barcode (Required)
    :param title str:
    :param author str:
    :param volume str:
    :param call_number str:
    :param collection str: Must match collection code in system, or bibliographic location listed on collection code detail (for translation)
    :param material str: Must match material type in system, or bibliographic material type listed on material type detail (for translation)
    :param oclc str:
    :param issn str:
    :param isbn str:
    :param edition str:
    :param copy_number str:
    :param pages str:
    :param publisher str:
    :param pub_place str:
    :param pub_year str:
    :param physical_desc str:
    :param format str:
    :param packaging str:
    :param condition str:
    :param shared_contrib str: Shared Print Contributor
    :param item_type str:
    :param bib_location str:
    :param bib_item_status str:
    :param bib_item_code str:
    :param bib_level str:
    :param bib_item_id str:
    :param bib_record_nbr str:
    """

    barcode : str
    title : str = None
    author : str = None
    volume : str = None
    call_number : str = None
    collection : str = None
    material : str = None
    oclc : str = None
    issn : str = None
    isbn : str = None
    edition : str = None
    copy_number : str = None
    pages : str = None
    publisher : str = None
    pub_place : str = None
    pub_year : str = None
    physical_desc : str = None
    format : str = None
    packaging : str = None
    condition : str = None
    shared_contrib : str = None
    item_type : str = None
    bib_location : str = None
    bib_item_status : str = None
    bib_item_code : str = None
    bib_level : str = None
    bib_item_id : str = None
    bib_record_nbr : str = None
