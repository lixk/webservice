import json

users = [{'id': 1, 'name': '小明'}, {'id': 2, 'name': '花花'}, {'id': '花花&id=123', 'name': '花花'}]


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


def _private_function():
    pass
