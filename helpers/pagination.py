from functools import wraps

from flask import request, abort


def extract_pagination_params():
    current_page = int(request.args.get('page'))
    per_page = int(request.args.get('perPage'))
    return {'current_page': current_page, 'per_page': per_page}


def get_per_page(current, default):
    if current is None:
        return default
    return current


def paginated_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Do something with your request here
        pagination_info = extract_pagination_params()
        pagination_info['sort_field'] = request.args.get('sortField')
        pagination_info['sort_order'] = request.args.get('sortOrder')
        return f(pagination_info, *args, **kwargs)

    return decorated_function
