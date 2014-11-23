from flask import Flask, render_template
from flask.ext.restful import Api, reqparse, Resource
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps

app = Flask(__name__)
# app.config["APPLICATION_ROOT"] ="/api"
app.config['MONGO_DBNAME'] = "music"
api = Api(app)
mongo = PyMongo(app)


parser = reqparse.RequestParser()
parser.add_argument('title', type=str)

@app.route("/")
def index():
    songs = mongo.db.songs.find().sort([( "points", 1 )])
    return render_template("haaletus.html", songs=songs)


class Song(Resource):
    def get(self, song_id):
        song = mongo.db.songs.find_one_or_404({'_id': song_id})
        return dumps(song)


class SongList(Resource):
    def get(self):
        return dict(mongo.db.songs.find().sort([( "points", 1 )]))
        #return {"id1": {"title": "Rick Astley - Never Gonna Give You Up", "points": 6}}
    def post(self):
        args = parser.parse_args()
        print(args)
        song_id = mongo.db.songs.insert({"title": args["title"], "points": 1})
        return Song.get(self, song_id)

api.add_resource(SongList, '/songs/')
api.add_resource(Song, "/songs/<string:song_id>")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
