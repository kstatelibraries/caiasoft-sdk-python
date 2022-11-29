# About
caiasoft - SDK for Connecting to CaiaSoft API

Caiasoft SDK is the Python library for writing code that interfaces with CaiaSoft Storage Management System.

# Usage

- [About](#about)
- [Usage](#usage)
- [Installation](#installation)
    - [Note](#note)
- [Getting an API Key](#getting-an-api-key)
- [Notes](#notes)
- [API Status](#api-status)
- [Contributing \& Bug Reporting](#contributing--bug-reporting)

# Installation

Use pip: (not setup yet)

```
pip install caiasoft-sdk-python
```

### Note 
>

>Alternatively the _latest_ version could be directly installed via GitHub:
>```
>pip install git+ssh://git@github.com:kstatelibraries/caiasoft-sdk-python.git
>```

# Getting an API Key


To use these libraries, you must first obtain an API token and password,
which can be done from within the Caiasoft Interface.


# Notes
The full API documentation can be found at https://portal.caiasoft.com/apiguide.php.

Documentation for the SDK can be found at ...

# API Status
| Method | Caiasoft API Endpoint |        Status          | Function Name            |
| ------ | --------------------- | ---------------------- | ------------------------ |
| GET    | /accessionedlist      | Implemented / No Tests | accessioned_items        |
| GET    | /accessioninfo        | Implemented / No Tests | accession_info           |
| GET    | /accessioned_active   | Implemented / No Tests | accession_items_active   |
| GET    | /bibmissing           | Implemented / No Tests | missing_bibfield         |
| GET    | /bibmissing_bydate    | Implemented / No Tests | missing_bibfield_bydate  |
| GET    | /circstoplist         | Implemented / No Tests | circ_stop_list           |
| GET    | /item                 | Implemented / No Tests | item_info                |
| GET    | /itemloc              | Implemented / No Tests | item_loc                 |
| GET    | /itemstatus           | Implemented / No Tests | item_status              |
| GET    | /refiledlist          | Implemented / No Tests | refiled_list             |
| GET    | /retrievedlist        | Implemented / No Tests | retrieved_list           |
| POST   | /attributefile        | Missing                | |
| POST   | /incomingfile         | Missing                | |
| POST   | /requestfile          | Missing                | |
| POST   | /circrequests         | Implemented / No Tests | circulation_request      |
| POST   | /incomingitems        | Implemented / No Tests | incoming_items           |
| POST   | /itemupdates          | Implemented / No Tests | item_updates             |
| POST   | /itemsbybarcode       | Implemented / No Tests | items_by_barcode         |
| POST   | /itemloclist          | Implemented / No Tests | item_location_by_barcode |

# Contributing & Bug Reporting

If you find a bug, please submit it through the `GitHub issues page`_.

Pull requests are welcome!

.. _`GitHub issues page`: https://github.com/kstatelibraries/caiasoft-sdk-python/issues
