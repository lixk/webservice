from PyInstaller.__main__ import run
from server import SERVICE


if __name__ == '__main__':
    opts = ['server.py', '-F', '-w', '--icon=bin/favicon.ico', '-y']
    for service_name in SERVICE.keys():
        opts.append('--hidden-import=%s' % service_name[0: service_name.rfind('.')])

    run(opts)
