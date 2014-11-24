from flask import Flask, render_template, redirect, url_for, Request
from flask.ext.restful import Api, reqparse, Resource
from flask.ext.pymongo import PyMongo
from tools import jsonify


app = Flask(__name__)
# app.config["APPLICATION_ROOT"] ="/api"
app.config['MONGO_DBNAME'] = "music"
api = Api(app)
mongo = PyMongo(app)


@app.route("/", defaults={'page': 1})
@app.route("/page/<int:page>")
def index(page):
    page -= 1
    page_size = 10
    songs = mongo.db.songs.find().sort([( "points", -1 )])#.skip(page_size*page).limit(page_size)
    return render_template("haaletus.html", songs=songs)


@app.route("/admin")
def admin():
    songs = mongo.db.songs.find().sort([( "points", -1 )])
    return render_template("admin.html", songs=songs)

@app.route("/about")
def about():
    return render_template("about.html")

class Song(Resource):
    vote_parser = reqparse.RequestParser()
    vote_parser.add_argument('vote', type=str, required=True)

    def get(self, song_id):
        song = mongo.db.songs.find_one_or_404({'_id': song_id})
        return jsonify(song)

    def delete(self, song_id):
        song = mongo.db.songs.remove({'_id': song_id})
        return song

    def patch(self, song_id):
        args = self.vote_parser.parse_args()
        #song = mongo.db.songs.find_one_or_404({'_id': song_id})
        if args["vote"] == "down":
            r = mongo.db.songs.find_and_modify({"_id": song_id, 
                "points":song["points"]}, {"$inc": {"points": -1}}, new=True)
        elif args["vote"] == "up":
            r = mongo.db.songs.find_and_modify({"_id": song_id, 
                "points":song["points"]}, {"$inc": {"points": +1}}, new=True)
        else:
            r = song
        return jsonify(r)


class SongList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', type=str, required=True)
    parser.add_argument('redirect', type=str)

    def get(self):
        return jsonify(mongo.db.songs.find().sort([( "points", -1 )]))

    def post(self):
        args = self.parser.parse_args()
        print(args)
        song_id = mongo.db.songs.insert({"title": args["title"], "points": 1})
        if args["redirect"] == "home":
            return redirect(url_for("index"))
        return Song.get(self, song_id)


api.add_resource(SongList, '/songs/')
api.add_resource(Song, "/songs/<ObjectId:song_id>")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
