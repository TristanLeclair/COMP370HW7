import argparse
import json
from pathlib import Path
import warnings

from bs4 import BeautifulSoup
import requests

warnings.filterwarnings(
    "ignore", category=UserWarning, module="bs4"
)  # ignore bs4 warnings about decoding utf-8


CACHING = True
LOGGING = True

URL_BASE = "https://montrealgazette.com"
URL_FRONT_PAGE = "{}/category/news/".format(URL_BASE)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
}


def log(msg):
    if LOGGING:
        print(msg)


def send_request(url):
    log(f"Sending request to {url}")
    return requests.get(url, headers=headers).content


def soupify(url):
    if CACHING:
        fpath = Path(f"cache/{url.replace('/', '_')}.html")
        if fpath.exists():
            with open(fpath, "r") as f:
                page = f.read()
        else:
            page = send_request(url)
            # create cache file
            fpath.parent.mkdir(parents=True, exist_ok=True)
            with open(fpath, "w") as f:
                f.write(page.decode("utf-8"))
    else:
        page = send_request(url)

    soup = BeautifulSoup(page, "html.parser", from_encoding="utf-8")
    return soup


def fetch_front_page():
    return soupify(URL_FRONT_PAGE)


def find_trending_links(soup):
    widgets = soup.find("div", class_="list-widget-trending")
    link_classes = widgets.find_all(class_="article-card__link")
    links = [link["href"] for link in link_classes]
    return links


def scrape_trending_link(link):
    URL = "{}{}".format(URL_BASE, link)

    soup = soupify(URL)

    title = soup.find("h1", class_="article-title")
    opening_blurb = soup.find("p", class_="article-subtitle")
    meta = soup.find("div", class_="article-meta")
    publication_date = meta.find("span", class_="published-date__since")
    author_link = meta.find("span", class_="published-by__author")
    author = author_link.find("a")

    info = {
        "title": title.text,
        "publication_date": publication_date.text,
        "author": author.text,
        "blurb": opening_blurb.text,
    }
    return info


def parse_args():
    global CACHING, LOGGING
    parser = argparse.ArgumentParser(
        description="Collect trending articles from the Montreal Gazette",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-o", metavar="<output file>", help="file to write to", required=True, default="trending.json"
    )
    # add optional argument for caching
    parser.add_argument(
        "--cache",
        action=argparse.BooleanOptionalAction,
        help="Toggle caching",
        default=True,
    )
    # add optional argument for logging
    parser.add_argument(
        # "-l", metavar="<log>", help="enable logging", required=False, default=LOGGING, type=bool
        "--log",
        action=argparse.BooleanOptionalAction,
        help="Toggle logging",
        default=False,
    )
    args = parser.parse_args()
    filename = args.o
    CACHING = args.cache
    LOGGING = args.log
    return filename


def main():
    filename = parse_args()

    front_page = fetch_front_page()

    links = find_trending_links(front_page)

    articles = []
    for link in links:
        info = scrape_trending_link(link)
        articles.append(info)

    json.dump(articles, open(filename, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
