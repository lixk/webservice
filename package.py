from PyInstaller.__main__ import run

import server

if __name__ == '__main__':
    opts = ['window.py', '-F', '-w', '--icon=bin/favicon.ico', '-y', '--distpath=out', '--specpath=out']
    server.init_service()
    for service_name in server.SERVICE.keys():
        opts.append('--hidden-import=%s' % service_name[0: service_name.rfind('.')])

    run(opts)
