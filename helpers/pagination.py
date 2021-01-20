from functools import wraps

from flask import request, abort


def extract_pagination_params():
    current_page = request.args.get('page')
    if current_page is not None:
        current_page = int(current_page)
    else:
        current_page = 1

    per_page = request.args.get('perPage')
    if per_page is not None:
        per_page = int(per_page)
    else:
        per_page = 10

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
        if request.args.get('sortField') is not None:
            pagination_info['sort_field'] = request.args.get('sortField')
        if request.args.get('sortOrder') is not None:
            pagination_info['sort_order'] = request.args.get('sortOrder')
        if request.args.get('getAll') is not None:
            pagination_info['get_all'] = request.args.get('getAll')
        return f(pagination_info, *args, **kwargs)

    return decorated_function
