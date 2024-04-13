import os
from flask import Flask
import flask_admin as admin
from flask_admin.contrib.peewee import ModelView
from huey import RedisHuey, crontab

from models import SavedLink, SearchTerm
from searcher import FeedSearcher, RedditSearcher

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "\xf5\xa7\xec\xd0I\xe3\x9aLMB\xd6\xa9F\x8e\x03\x8a]9\xb4\xc8\x1cm\x08\xfc"
)
app.config["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

huey = RedisHuey("news-digest", url=app.config["REDIS_URL"])

admin = admin.Admin(app, name="News Digest")

SEARCHERS = [
    FeedSearcher("https://news.ycombinator.com/rss"),
    RedditSearcher("http://www.reddit.com/r/programming/hot.json"),
    RedditSearcher("http://www.reddit.com/r/Python/hot.json"),
]


class SearchTermAdmin(ModelView):
    pass


class SavedLinkAdmin(ModelView):
    pass


admin.add_view(SearchTermAdmin(SearchTerm))
admin.add_view(SavedLinkAdmin(SavedLink))


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@huey.task()
def add_numbers(a, b):
    return a + b


@huey.periodic_task(crontab(minute="0", hour="7"))
def content_search():
    logger = app.logger
    query = SearchTerm.select()
    links = []

    for searcher in SEARCHERS:
        try:
            results = searcher.search(query)
        except:
            logger.exception("Error fetching %s", searcher.url)
        else:
            for result in results:
                exists = SavedLink.select().where(SavedLink.url == result.url).exists()
                if not exists:
                    SavedLink.create(title=result.title, url=result.url)
                    links.append(result)

    if links:
        digest = "\n".join('"%s"  ->  %s' % (link.title, link.url) for link in links)
        # send_email(my_email_address, "Article digest", digest)


if __name__ == "__main__":
    try:
        SearchTerm.create_table()
        SavedLink.create_table()
    except:
        pass
    app.run(debug=True)
