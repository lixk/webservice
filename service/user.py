import json
import os

users = [{'id': 1, 'name': 'Tom'}, {'id': 2, 'name': '花花'}]


def get_user_list():
    """
    get user list

    :return:
    """
    return json.dumps(users, ensure_ascii=False)


def get_user_by_id(id):
    """
    get user by id
    :param id: user id
    :return:
    """
    for user in users:
        print(id)
        if user['id'] == int(id):
            return json.dumps(user, ensure_ascii=False)
    return None


def upload(file):
    """
    upload user info

    :param file:
    :return:
    """
    # print(file.name, file.filename, os.path.split(file.raw_filename)[1])
    # print(dir(file))
    path = 'data/{0}'.format(os.path.split(file.raw_filename)[1])
    file.save(path, True)
    import webbrowser
    webbrowser.open('localhost')
    return path


def _private_function():
    pass
