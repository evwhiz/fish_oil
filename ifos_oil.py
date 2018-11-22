import datetime as dt
from lxml import html
import os
import requests
import time
import urllib


IFOS_SRC_URL = "http://consumer.nutrasource.ca/ifos/product-reports/"


def get_etree(url=IFOS_SRC_URL):
    """
    Returns report page's html.Element
    """
    page = requests.get(url)
    etree = html.fromstring(page.content)
    return etree


def validate_file(filename):
    print("filename", filename)
    if os.path.isfile(filename):
        now = time.now()
        created = os.stat.file(filename)
        print("now", now, "created", created)
        return now - created >= 60 * 60 * 24
    else:
        return False


def get_report_urls(etree):
    """
    Returns list of report link strings
    """
    raw_reports = etree.xpath('//a[contains(@href,"/files/")]/@href')
    prefix = "http://consumer.nutrasource.ca"
    report_links = [prefix + urllib.parse.quote(url, safe="/") for url in raw_reports]
    return report_links


def get_report_filename(url):
    return urllib.parse.unquote(url.split("/files/")[-1]).replace(" ", "")


def archive_report(report_url):
    response = requests.get(report_url)
    filename = "./tmp/" + get_report_filename(report_url)  
    if os.path.isfile(filename):
        print("Writing file to {}".format(filename))
        with open(filename, "wb") as f:
                f.write(response.content)


###########
# PYTESTS #
###########
TEST_SRC_URL = IFOS_SRC_URL
TEST_REPORT_URL = r"http://consumer.nutrasource.ca/files/IFOS%20See%20Yourself%20Well%20Omega%203%201500%20Lemon.pdf"


def test_get_etree(url=TEST_SRC_URL):
    global TEST_ETREE
    TEST_ETREE = get_etree()
    title = TEST_ETREE.xpath("//html/head/title")[0].text
    assert type(TEST_ETREE) == html.HtmlElement
    assert "Product Reports" in title


def test_get_report_urls():
    global TEST_LINKS
    TEST_LINKS = get_report_urls(TEST_ETREE)
    print("Found", len(TEST_LINKS), "links")
    print(TEST_LINKS[0])
    assert len(TEST_LINKS) > 0
    assert ".pdf" in TEST_LINKS[0]
    for link in TEST_LINKS:
        assert "http://consumer.nutrasource.ca/files/" in link
        assert link[-4:] == ".pdf"
        assert " " not in link


def test_get_report_filename():
    global TEST_FILENAME
    TEST_FILENAME = get_report_filename(TEST_LINKS[0])
    
    # TODO: ASSERTIONS like no weird characters, spaces, what nots

    assert TEST_FILENAME == "IFOSSeeYourselfWellOmega31500Lemon.pdf"


def test_archive_report():
    global TEST_ARCHIVE_REPORT
    TEST_ARCHIVE_REPORT = (get_report_filename(TEST_REPORT_URL))
    assert os.path.isfile("./tmp/IFOSSeeYourselfWellOmega31500Lemon.pdf")


def test_validate_file():
    archive_report(get_report_filename(TEST_REPORT_URL))
    assert validate_file("./tmp/IFOSSeeYourselfWellOmega31500Lemon.pdf")
