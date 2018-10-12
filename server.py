import glob
import importlib
import inspect
import json
import logging
import os
import socket
import threading
import time

from bottle import request, Bottle, response, run, template
from gevent import monkey

monkey.patch_all()
import sys

print(os.getcwd(), sys.argv, os.path.split(sys.argv[0]))
sys.path.append(os.path.split(sys.argv[0])[0])

SERVICE = {}
SERVICE_PACKAGE = 'service'
VIEW_PACKAGE = 'view'
EXT = '.py'  # file ext name
PORT = 80  # default server port
app = Bottle()

# load service modules and functions
files = glob.glob(SERVICE_PACKAGE + '/**')
print(files)
for f in files:
    if not f.endswith(EXT):
        continue
    module_name = f.replace(os.path.sep, '.')[0:-len(EXT)]
    module = importlib.import_module(module_name)
    # extract Non-private functions
    for key, value in module.__dict__.items():
        if not key.startswith('_') and inspect.isfunction(value):
            service_name = (module_name + '.' + key).replace('.', '/')
            SERVICE[service_name] = value

# service js template
SERVICE_JS = r'''
function initService(name) {
    var variables = name.split('.');
    var p = window;
    for (var i = 0; i < variables.length; i++) {
        var v = variables[i];
        p[v] = p[v] || {};
        p = p[v];
    }
}

function bindService(url, data, success, error) {
    var xhr = new XMLHttpRequest();
    var formData = new FormData();
    for(var key in data) { formData.append(key, data[key]); }
    success = success || function (data) {};
    error = error || function (e) { console.error(e) };
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                success(xhr.response);
            } else {
                error(xhr.response);
            }
        }
    }
    xhr.open("POST", url, true);
    xhr.send(formData);
}

'''


@app.route('/service.js')
def service():
    global SERVICE_JS
    js = SERVICE_JS

    scheme = request.urlparts.scheme
    netloc = request.urlparts.netloc

    # register service to js
    for name in SERVICE.keys():
        js += 'initService("%s");\n' % name.replace('/', '.')

    for name, func in SERVICE.items():
        # service url
        url = '{0}://{1}/{2}'.format(scheme, netloc, name)
        # js function doc
        doc = inspect.getdoc(func)
        if doc:
            js += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
        # js function args
        args = inspect.getfullargspec(func).args
        js_args = ', '.join(args)
        if js_args:
            js_args += ', '
        js_args += 'success, error'
        data = '{%s}' % ', '.join(['{0}:{0}'.format(arg) for arg in args])
        # create js function
        js += 'window.%(name)s = function(%(js_args)s){ bindService("%(url)s", %(data)s, success, error); }\n' % {
            "name": name.replace('/', '.'),
            "js_args": js_args,
            "url": url,
            "data": data
        }

    # set Content-Type
    response.headers['Content-Type'] = 'application/javascript'

    return js


@app.route('/<path:path>', method=['POST'])
def dispatcher(path):
    params = dict(request.POST)
    print(path, params)
    service_function = SERVICE.get(path, None)
    if service_function is None:
        return json.dumps({'code': 404, 'message': 'Service "%s" not found!' % path}, ensure_ascii=False)
    try:
        return service_function(**params)
    except Exception as e:
        logging.error('Server error:', e)
        return json.dumps({'code': 500, 'message': 'Server error: %s' % e}, ensure_ascii=False)


@app.route('/view/<path:path>')
def view(path):
    print(os.path.join(VIEW_PACKAGE, path))
    return template(os.path.join(VIEW_PACKAGE, path), {'port': PORT})


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


# server startup callback function
def on_startup():
    import subprocess
    import webbrowser
    subprocess.Popen('bin/easy-window.exe -url http://127.0.0.1:%s/view/index.html' % PORT)
    # webbrowser.open('http://127.0.0.1:%s/view/index.html' % PORT)


# check if the server has startup
def check_startup():
    while True:
        try:
            sk = socket.socket()
            sk.connect(('127.0.0.1', PORT))
            sk.close()
            break
        except ConnectionError:
            time.sleep(0.1)
    on_startup()


if __name__ == '__main__':
    threading.Thread(target=check_startup).start()
    # startup server
    for i in range(30):
        try:
            run(app=app, host='0.0.0.0', port=PORT, server='gevent')
        except OSError:
            PORT += 1
