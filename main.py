from flask import Flask, render_template, redirect, url_for, Request
from flask import make_response, request
from flask.ext.restful import Api, reqparse, Resource
from flask.ext.pymongo import PyMongo, ObjectId
from tools import jsonify
from datetime import datetime


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
    vote_parser.add_argument('voter_id', type=str, location='cookies')

    def get(self, song_id):
        song = mongo.db.songs.find_one_or_404({'_id': song_id})
        return jsonify(song)

    def delete(self, song_id):
        song = mongo.db.songs.remove({'_id': song_id})
        return song

    def patch(self, song_id):
        args = self.vote_parser.parse_args()
        votes = {"up": +1,
                "down": -1}
        # check input
        if args["vote"] not in votes:
            return {"error": "wrong vote value"}, 400

        # is the user a new user
        if not args["voter_id"]:
            # cast a vote
            r = mongo.db.songs.find_and_modify({"_id": song_id}, 
                {"$inc": {"points": votes[args["vote"]]}}, new=True)
            # that song didnt exist
            if not r:
                return {"error": "Song does not exists"}, 404
            # create a new user
            voter = mongo.db.voters.insert({"voted_songs":{str(r["_id"]):args["vote"]}, 
                    "created_at":datetime.now()})
            # create a responce with user cookie
            resp = make_response(jsonify(r))
            resp.set_cookie("voter_id", value=str(voter), max_age=86400)
        # user has voted before aka old user
        else:
            # load user
            voter = mongo.db.voters.find_one({"_id":ObjectId(args["voter_id"])})
            vote = votes[args["vote"]]
            print(voter["voted_songs"])
            print(song_id)
            # if user has voted on that song before
            if str(song_id) in voter["voted_songs"].keys():
                if args["vote"] != voter["voted_songs"][str(song_id)]:
                    # undo last vote and cast a new vote
                    vote = -vote-vote
                    update = mongo.db.voters.update({"_id":voter["_id"]}, 
                        {"$set":{'voted_songs.'+str(song_id):args['vote']}})
                    print("update set", update)
                elif args["vote"] == voter["voted_songs"][str(song_id)]:
                    # undo last vote
                    vote = -vote
                    update = mongo.db.voters.update({"_id":voter["_id"]}, 
                        {"$unset":'voted_songs.'+str(song_id)})
                    print("update unset", update)
                # actually cast that vote
                else:
                    return {"error":"wtf"}, 500
                r = mongo.db.songs.find_and_modify({"_id": song_id}, 
                    {"$inc": {"points": vote}}, new=True)
                if not r:
                    # that song didnt exist
                    return {"error": "Song does not exists"}, 404
                return jsonify(r)

            # user hasn't voted before
            else:

                return {"error": "not implemented"}, 500
        return resp


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
