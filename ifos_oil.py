from datetime import date
from lxml import html
import os
import pathlib
import requests
import time
import urllib


IFOS_SRC_URL = "http://consumer.nutrasource.ca/ifos/product-reports/"
    

def get_etree(url):
    """
    Returns report page's html.Element
    """
    page = requests.get(url)
    etree = html.fromstring(page.content)
    return etree


def get_report_urls(etree):
    "Returns list of report link strings"
    raw_reports = etree.xpath('//a[contains(@href,"/files/")]/@href')
    prefix = "http://consumer.nutrasource.ca"
    report_links = [prefix + urllib.parse.quote(url, safe="/") for url in raw_reports]
    return report_links


def get_report_filename(url):
    today_stamp = str(date.today())  # example: "2018-11-22"
    filename = today_stamp + "-" + urllib.parse.unquote(url.split("/files/")[-1])
    filename = filename.replace(" ", "").replace(",", "")
    return filename


def validate_file(filename, epoch_age=60 * 60 * 24 * 30):
    "Returns True if file exists and is younger than epoch_age"
    if os.path.isfile(filename):
        now = time.time()
        created = os.stat(filename).st_mtime
        file_age = now - created
        print("file_age:{} <= epoch_age:{}".format(file_age, epoch_age))
        return file_age <= epoch_age
    else:
        return False


def archive_report(report_url, epoch_age=0, archive_dir="./tmp/"):
    """
    Validates existense of file of at least the epoch_age,
    else collects and writes a new report file to the archive_dir
    """
    filename = archive_dir + get_report_filename(report_url)
    if not validate_file(filename, epoch_age=epoch_age):
        if not os.path.exists(archive_dir):
            pathlib.Path(archive_dir).mkdir(parents=True, exist_ok=True)
        response = requests.get(report_url)
        print("Writing file to {}".format(filename))
        with open(filename, "wb") as f:
            f.write(response.content)


def expell_ifos_oil(archive_dir, epoch_age=60 * 60 * 24 * 30, pause=5, number=0):
    "Gets new files if files older than epoch_age. Default epoch_age is 30 days"
    etree = get_etree(IFOS_SRC_URL)
    report_urls = get_report_urls(etree)
#     if not number == 0:
#         number = min(number, len(report_urls))
#         report_urls = report_urls[:number]
    for report_url in report_urls[:min(number, len(report_urls))]:
        archive_report(report_url, epoch_age=epoch_age, archive_dir=archive_dir)
        time.sleep(pause)


###########
# PYTESTS #
###########
TEST_SRC_URL = IFOS_SRC_URL
TEST_REPORT_URL = r"http://consumer.nutrasource.ca/files/IFOS%20See%20Yourself%20Well%20Omega%203%201500%20Lemon.pdf"
TEST_ARCHIVE_DIR = "./tmp/"


def test_get_etree():
    global TEST_ETREE
    TEST_ETREE = get_etree(url=TEST_SRC_URL)
    title = TEST_ETREE.xpath("//html/head/title")[0].text
    assert type(TEST_ETREE) == html.HtmlElement
    assert "Product Reports" in title


def test_get_report_urls():
    global TEST_REPORT_URLS
    TEST_REPORT_URLS = get_report_urls(TEST_ETREE)
    assert len(TEST_REPORT_URLS) > 0
    assert ".pdf" in TEST_REPORT_URLS[0]
    for test_report_url in TEST_REPORT_URLS:
        assert "http://consumer.nutrasource.ca/files/" in test_report_url
        assert test_report_url[-4:] == ".pdf"
        assert " " not in test_report_url


def test_get_report_filename():
    print("TEST_REPORT_URLS[0]", TEST_REPORT_URLS[0])
    global TEST_FILENAME
    TEST_FILENAME = get_report_filename(TEST_REPORT_URLS[0])
    assert TEST_FILENAME == str(date.today()) + "-" + "IFOSSeeYourselfWellOmega31500Lemon.pdf"


def test_archive_report():
    archive_report(TEST_REPORT_URLS[0], epoch_age=0, archive_dir=TEST_ARCHIVE_DIR)
    assert os.path.isfile(TEST_ARCHIVE_DIR + TEST_FILENAME)


def test_validate_file():
    assert validate_file(TEST_ARCHIVE_DIR + TEST_FILENAME)
    assert not validate_file(TEST_ARCHIVE_DIR + TEST_FILENAME, epoch_age=-1)
