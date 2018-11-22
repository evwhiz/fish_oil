from lxml import html
import os
import requests
import urllib
import urllib.parse


IFOS_URL = "http://consumer.nutrasource.ca/ifos/product-reports/"


def get_etree(url=IFOS_URL):
    """
    Returns report page's html.Element
    """
    page = requests.get(url)
    etree = html.fromstring(page.content)
    return etree


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
    print("Writing file to {}".format(filename))
    with open(filename, "wb") as f:
        f.write(response.content)


###########
# PYTESTS #
###########


def test_get_etree(url=IFOS_URL):
    global TEST_ETREE
    TEST_ETREE = get_etree()
    title = TEST_ETREE.xpath("//html/head/title")[0].text
    assert type(TEST_ETREE) == html.HtmlElement
    assert "Product Reports" in title


def test_get_report_urls():
    links = get_report_urls(TEST_ETREE)
    print("Found", len(links), "links")
    print(links[0])
    assert len(links) > 0
    assert ".pdf" in links[0]
    for link in links:
        assert "http://consumer.nutrasource.ca/files/" in link
        assert link[-4:] == ".pdf"
        assert " " not in link


def test_get_report_filename():
    test_report_url = r"http://consumer.nutrasource.ca/files/IFOS%20See%20Yourself%20Well%20Omega%203%201500%20Lemon.pdf"
    filename = get_report_filename(test_report_url)
    assert filename == "IFOSSeeYourselfWellOmega31500Lemon.pdf"


def test_archive_report():
    test_report_url = r"http://consumer.nutrasource.ca/files/IFOS%20See%20Yourself%20Well%20Omega%203%201500%20Lemon.pdf" 
    archive_report(test_report_url)
    assert os.path.isfile("./tmp/IFOSSeeYourselfWellOmega31500Lemon.pdf")