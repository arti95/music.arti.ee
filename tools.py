from flask.json import dumps
from bson.json_util import _json_convert
from werkzeug import Response

def jsonify(obj, *args, **kwargs):
    """ jsonify with support for MongoDB ObjectId
    """
    return Response(dumps(_json_convert(obj),*args, **kwargs), mimetype='application/json')