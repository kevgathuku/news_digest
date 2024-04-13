from flask import Flask
import flask_admin as admin
from flask_admin.contrib.peewee import ModelView
from models import SavedLink, SearchTerm

app = Flask(__name__)
app.config['SECRET_KEY'] = "\xf5\xa7\xec\xd0I\xe3\x9aLMB\xd6\xa9F\x8e\x03\x8a]9\xb4\xc8\x1cm\x08\xfc"

admin = admin.Admin(app, name="News Digest")


class SearchTermAdmin(ModelView):
    pass


class SavedLinkAdmin(ModelView):
    pass


admin.add_view(SearchTermAdmin(SearchTerm))
admin.add_view(SavedLinkAdmin(SavedLink))


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    try:
        SearchTerm.create_table()
        SavedLink.create_table()
    except:
        pass
    app.run(debug=True)
