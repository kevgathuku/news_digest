import json
from xml.etree import ElementTree as etree
from collections import namedtuple

import requests

Link = namedtuple("Link", ("title", "url"))


class Searcher(object):
    user_agent = "PythonicHacks/0.1"

    def __init__(self, url):
        self.url = url

    def fetch(self):
        response = requests.get(self.url, headers={"User-Agent": self.user_agent})
        return response.content

    def search(self, search_terms):
        content = self.fetch()
        for link in self.extract_links(content):
            for search_term in search_terms:
                if search_term.test(link.title.lower()):
                    yield link
                    break

    def extract_links(self, content):
        raise NotImplementedError


class FeedSearcher(Searcher):
    def extract_links(self, content):
        tree = etree.fromstring(content)
        articles = tree.findall("channel/item")
        for article in articles:
            yield Link(title=article.findtext("title"), url=article.findtext("link"))


class RedditSearcher(Searcher):
    def extract_links(self, content):
        content = json.loads(content)
        links = content["data"]["children"]
        for link in links:
            link_data = link["data"]
            if link_data["selftext"] == "":
                yield Link(title=link_data["title"], url=link_data["url"])
