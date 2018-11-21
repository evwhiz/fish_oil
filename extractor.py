from lxml import html
import requests
import urllib
import urllib.parse


URL = "http://consumer.nutrasource.ca/ifos/product-reports/"


def get_etree(url=URL):
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
    print(raw_reports[0])
    prefix = "http://consumer.nutrasource.ca"
    report_links = [prefix + urllib.parse.quote_plus(url) for url in raw_reports]
    return report_links


# def encode_url(url):
#     """
#     Returns
#         url(str): string replaced
#     """
#     url = url.replace(" ", "%20")
#     url = url.replace("!", "%21")
#     url = url.replace(",", "%2C")
#     return url

# PYTEST
def test_get_etree(url=URL):
    global TEST_ETREE
    TEST_ETREE = get_etree()
    title = TEST_ETREE.xpath('//html/head/title')[0].text
    assert type(TEST_ETREE) == html.HtmlElement
    assert "Product Reports" in title


def test_get_report_links():
    links = get_report_urls(TEST_ETREE)
    print(len(links))
    print(links[0])
    assert len(links) > 0
    assert ".pdf" in links[0] 