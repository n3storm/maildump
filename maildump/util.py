import json
import pkg_resources
import pytz
from datetime import datetime
from flask import current_app
from functools import wraps
from webassets.filter.cssprefixer import CSSPrefixer as _CSSPrefixer


UTC = pytz.timezone('UTC')


def _json_default(obj):
    if isinstance(obj, datetime):
        return UTC.localize(obj).isoformat()
    raise TypeError(repr(obj) + ' is not JSON serializable')


def json_dumps(obj):
    return json.dumps(obj, default=_json_default, indent=4)


def jsonify(*args, **kwargs):
    return current_app.response_class(json_dumps(dict(*args, **kwargs)), mimetype='application/json')


def bool_arg(arg):
    return arg in ('yes', 'true', '1')


def rest(f):
    """Decorator for simple REST endpoints.

    Functions must return one of these values:
    - a dict to jsonify
    - nothing for an empty 204 response
    - a tuple containing a status code and a dict to jsonify
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        ret = f(*args, **kwargs)
        if ret is None:
            response = jsonify()
            response.status_code = 204  # no content
        elif isinstance(ret, current_app.response_class):
            response = ret
        elif isinstance(ret, tuple):
            # code, result_dict|msg_string
            if isinstance(ret[1], basestring):
                response = jsonify(msg=ret[1])
            else:
                response = jsonify(**ret[1])
            response.status_code = ret[0]
        else:
            response = jsonify(**ret)
        return response

    return wrapper


def get_version():
    try:
        return 'v' + pkg_resources.get_distribution('maildump').version
    except pkg_resources.DistributionNotFound:
        return 'dev'


class CSSPrefixer(_CSSPrefixer):
    max_debug_level = None
