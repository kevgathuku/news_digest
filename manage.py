from flask.cli import with_appcontext

from app import app, send_email, SEARCHERS
from models import *


@with_appcontext
@app.cli.command("send_digest")
def send_digest():
    logger = app.logger
    query = SearchTerm.select()
    links = []

    for term in query:
        print("Search term:", term.phrase)

    for searcher in SEARCHERS:
        try:
            results = searcher.search(query)
        except:
            logger.exception("Error fetching %s", searcher.url)
        else:
            for result in results:
                print("result: ", result)
                exists = SavedLink.select().where(SavedLink.url == result.url).exists()
                if not exists:
                    SavedLink.create(title=result.title, url=result.url)
                    links.append(result)

    if links:
        print("Links: ", links)
        logger.info("Found %s links", len(links))
        digest = "\n".join('"%s"  ->  %s' % (link.title, link.url) for link in links)
        send_email("Your Latest Programming News digest", digest)


@app.cli.command("hello")
@with_appcontext
def hello():
    print("Hello, world!")


if __name__ == "__main__":
    app.run()
