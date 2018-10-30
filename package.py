from PyInstaller.__main__ import run

import py4js

if __name__ == '__main__':
    opts = ['window.py', '-F', '-w', '--icon=favicon.ico', '-y', '--distpath=out/dist', '--specpath=out']
    server = py4js.Server()
    for service_name in server.services.keys():
        opts.append('--hidden-import=%s' % service_name[0: service_name.rfind('.')])

    run(opts)
