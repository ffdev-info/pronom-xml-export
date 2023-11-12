"""Script to export PRONOM XML from PRONOM.

For more on the multiprocessing behavior:

    * Stack Overflow: https://stackoverflow.com/a/51814938

"""
import configparser as ConfigParser
import logging
import multiprocessing
import os
import time
from pathlib import Path
from typing import Final

import requests

# Set up logging.
logging.basicConfig(
    format="%(asctime)-15s %(levelname)s :: %(filename)s:%(lineno)s:%(funcName)s() :: %(message)s",  # noqa: E501
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Format logs using UTC time.
logging.Formatter.converter = time.gmtime


logger = logging.getLogger(__name__)


# Expected BOF bytes from XML export.
xml_string: Final[str] = "<?xml version="

# folder in which to place the download output
export_dir: Final[str] = "pronom-export"


puid_type_list = ["x-fmt", "fmt"]

config = ConfigParser.RawConfigParser()
config.read("pronom-xml-export.cfg")

# url through which to access Pronom data...
base_url: Final[str] = "https://www.nationalarchives.gov.uk/PRONOM/"


def download_and_save_puid(puid_filename_pair: tuple) -> None:
    """Perform the HTTP request and save routine to save the
    PRONOM record to disk.
    """
    puid_url, file_name = puid_filename_pair
    header = {"User-Agent": "exponentialDK-PRONOM-Export/0.0.0"}
    logger.info(puid_url)
    request = requests.get(puid_url, timeout=30, headers=header)
    test_string = request.text[:14]
    if not check_record(test_string):
        logger.info("not writing record: %s (%s)", file_name, test_string)
        return
    with open(file_name, "w", encoding="utf-8") as fmt_record:
        fmt_record.write(request.text)
    return


def get_ranges() -> dict:
    """Return the number of records for each PUID."""
    puid_dict = {}
    for puid_type in puid_type_list:
        puid_range = config.getint("puids", puid_type)
        if puid_range > 0:
            # plus one because zero-based indexes.
            puid_dict[puid_type] = puid_range + 1
    return puid_dict


def export_pronom_data():
    """Export PRONOM data and write locally"""
    puid_range_dict = get_ranges()
    for puid_type, puid_range in puid_range_dict.items():
        # Create a directory to write to.
        puid_type_url = base_url + puid_type + "/"
        new_dir = Path(os.path.join(export_dir, puid_type))
        new_dir.mkdir(parents=True, exist_ok=True)

        # Create a list of puid urls and filenames to save the outputs to.
        puid_filename_pairs = []
        for idx in range(1, puid_range):
            puid_url = f"{puid_type_url}{idx}.xml"
            file_name = new_dir / Path(f"{puid_type}{idx}.xml")
            puid_filename_pairs.append((puid_url, file_name))

        # Download PRONOM data.
        with multiprocessing.Pool() as pool:
            pool.map(download_and_save_puid, puid_filename_pairs)


def check_record(ffb: str) -> bool:
    """Ensure that we're downloading an XML record.

    NB. ffb == "first fourteen bytes"
    """
    if ffb == xml_string:
        return True
    return False


def main():
    """Primary entry point for this script."""
    # time script execution time roughly...
    t0 = time.perf_counter()
    export_pronom_data()
    logger.info("execution time: %s seconds", str(time.perf_counter() - t0))


if __name__ == "__main__":
    main()
