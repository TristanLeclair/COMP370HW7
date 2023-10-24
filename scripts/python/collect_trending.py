import argparse
import json

from bs4 import BeautifulSoup
import requests

URL_BASE = "https://montrealgazette.com"
URL_FRONT_PAGE = "{}/category/news/".format(URL_BASE)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
}


def soupify(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser", from_encoding="utf-8")
    return soup


def fetch_front_page():
    return soupify(URL_FRONT_PAGE)


def scrape_for_trending_links(soup):
    widgets = soup.find("div", class_="list-widget-trending")
    link_classes = widgets.find_all(class_="article-card__link")
    links = [link["href"] for link in link_classes]
    return links


def scrape_trending_link(link):
    URL = "{}{}".format(URL_BASE, link)

    soup = soupify(URL)

    # find title
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
    print(info)
    return info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", metavar="<output file>", help="file to write to", required=True
    )
    args = parser.parse_args()
    filename = args.o
    return filename


def main():
    filename = parse_args()

    front_page = fetch_front_page()

    links = scrape_for_trending_links(front_page)

    articles = []
    for link in links:
        info = scrape_trending_link(link)
        # add info to json file
        articles.append(info)

    json.dump(articles, open(filename, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()