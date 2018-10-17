import socket


def get_host_ip():
    """
    get host ip address
    获取本机IP地址

    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def is_port_used(ip, port):
    """
    check whether the port is used by other program
    检测端口是否被占用

    :param ip:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def get_available_port(default_port=5000):
    """
    get an available port
    获取一个可用端口

    :param default_port:
    :return:
    """
    ip = get_host_ip()
    port = default_port
    while is_port_used(ip, port):
        port += 1
    return port


if __name__ == '__main__':
    host_ip = get_host_ip()
    print(host_ip)
    print(is_port_used(host_ip, 80))
