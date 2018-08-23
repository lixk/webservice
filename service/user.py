import json

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
    print(file.name, file.filename)
    path = 'data/{0}'.format(file.filename)
    file.save(path)
    return path


def _private_function():
    pass
