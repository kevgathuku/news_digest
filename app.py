import os
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import flask_admin as admin
from huey import RedisHuey, crontab

from models import SavedLink, SearchTerm, SearchTermAdmin, SavedLinkAdmin
from searcher import FeedSearcher, RedditSearcher

app = Flask(__name__)

# config
app.config["SECRET_KEY"] = (
    "\xf5\xa7\xec\xd0I\xe3\x9aLMB\xd6\xa9F\x8e\x03\x8a]9\xb4\xc8\x1cm\x08\xfc"
)
app.config["REDIS_URL"] = os.environ.get("REDISCLOUD_URL", "redis://localhost:6379/0")
app.config.update(
    MAIL_SERVER="smtp.googlemail.com",
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.environ.get("MAIL_USERNAME"),
    MAIL_DEFAULT_RECIPIENT=os.environ.get("MAIL_RECIPIENT"),
)

# extensions
admin = admin.Admin(app, name="News Digest")
huey = RedisHuey("news-digest", url=app.config["REDIS_URL"])
mail = Mail(app)

admin.add_view(SearchTermAdmin(SearchTerm))
admin.add_view(SavedLinkAdmin(SavedLink))

SEARCHERS = [
    FeedSearcher("https://news.ycombinator.com/rss"),
    RedditSearcher("http://www.reddit.com/r/programming/hot.json"),
    RedditSearcher("http://www.reddit.com/r/Python/hot.json"),
    RedditSearcher("https://www.reddit.com/r/ruby/hot.json"),
]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@huey.task()
def add_numbers(a, b):
    return a + b


def send_email(subject, text_body):
    with app.app_context():
        msg = Message(
            subject,
            body=text_body,
            recipients=[app.config["MAIL_DEFAULT_RECIPIENT"]],
            sender=("News Digest", app.config["MAIL_USERNAME"]),
        )
        mail.send(msg)


@app.route("/task", methods=["POST"])
def task():
    # Get POST data
    data = request.get_json()
    param = data.get("type")

    if param == "email":
        send_email("Testing the Connection", "Hello, here is your latest news digest")
        return jsonify({"message": "Sent the email!"}), 202
    else:
        return (
            jsonify({"error": 'Failed to start task. Requires search_type of "task"'}),
            500,
        )


@huey.periodic_task(crontab(minute="21", hour="05"))
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
        logger.info("Found %s links", len(links))
        digest = "\n".join('"%s"  ->  %s' % (link.title, link.url) for link in links)
        send_email("Your Latest Programming News digest", digest)


if __name__ == "__main__":
    try:
        SearchTerm.create_table()
        SavedLink.create_table()
    except:
        pass
    app.run(debug=True, port=8080)
