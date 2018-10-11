if __name__ == '__main__':
    from PyInstaller.__main__ import run

    opts = ['server.py', '-F', '-w', '--icon=bin/favicon.ico']
    run(opts)
