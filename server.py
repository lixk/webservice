import glob
import importlib
import inspect
import json
import logging
import os
import socket
from window import Window

from bottle import request, Bottle, response, run, template

SERVICE = {}
SERVICE_PACKAGE = 'service'
VIEW_PACKAGE = 'view'
SERVICE_JS_PATH = VIEW_PACKAGE + '/service.js'
SCHEMA = 'http'
PORT = 54737  # default server port
os.makedirs(SERVICE_PACKAGE, exist_ok=True)
os.makedirs(VIEW_PACKAGE, exist_ok=True)
app = Bottle()

# load service modules and functions
MODULE_FILES = glob.glob(SERVICE_PACKAGE + '/**.py', recursive=True)
print('module files:', MODULE_FILES)
for module_path in MODULE_FILES:
    module_name = os.path.splitext(module_path)[0].replace(os.path.sep, '.')
    module = importlib.import_module(module_name)
    # extract Non-private functions as service
    for key, value in module.__dict__.items():
        if not key.startswith('_') and inspect.isfunction(value):
            service_name = (module_name + '.' + key)
            SERVICE[service_name] = value
print('services:', SERVICE)


def create_service_js(scheme, host, port):
    script = r'''//create service function
function createService(name) {
    var variables = name.split('.');
    var p = window;
    for (var i = 0; i < variables.length; i++) {
        var v = variables[i];
        p[v] = p[v] || {};
        p = p[v];
    }
}

//init service function
function initService(url, data, success, error) {
    var xhr = new XMLHttpRequest();
    var formData = new FormData();
    for(var key in data) { formData.append(key, data[key]); }
    success = success || function (data) {};
    error = error || function (e) { console.error(e) };
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var r = eval('('+xhr.response+')');
                if(r.code == 200){
                    success(r.data);
                } else {error(r.message)}
            } else {
                error(xhr.response);
            }
        }
    }
    xhr.open("POST", url, true);
    xhr.send(formData);
}

'''

    # register service to js
    script += '\n/********************** create service ****************************/\n'
    for service_name in SERVICE.keys():
        script += 'createService("%s");\n' % service_name
    script += '\n/*********************** init service ****************************/\n'
    for service_name, service in SERVICE.items():
        # service url
        url = '{0}://{1}:{2}/{3}'.format(scheme, host, port, service_name.replace('.', '/'))
        # js function doc
        doc = inspect.getdoc(service)
        if doc:
            script += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
        # js function args
        args = inspect.getfullargspec(service).args
        js_args = ', '.join(args)
        if js_args:
            js_args += ', '
        js_args += 'success, error'
        data = '{%s}' % ', '.join(['{0}:{0}'.format(arg) for arg in args])
        # create js function
        script += 'window.%(name)s = function(%(js_args)s){ initService("%(url)s", %(data)s, success, error); }\n' % {
            "name": service_name,
            "js_args": js_args,
            "url": url,
            "data": data
        }

    # set Content-Type
    response.headers['Content-Type'] = 'application/javascript'
    # write script to js file
    with open(SERVICE_JS_PATH, mode='w', encoding='utf-8') as file:
        file.write(script)


@app.route('/<path:path>', method=['POST'])
def dispatcher(path):
    params = dict(request.POST)
    print(path, params)
    service_function = SERVICE.get(path.replace('/', '.'), None)
    if service_function is None:
        return json.dumps({'code': 404, 'message': 'Service "%s" not found!' % path}, ensure_ascii=False)
    try:
        return json.dumps({'code': 200, 'data': service_function(**params)}, ensure_ascii=False)
    except Exception as e:
        logging.error('Server error:', e)
        return json.dumps({'code': 500, 'message': 'Server error: %s' % e}, ensure_ascii=False)


@app.route('/startup')
def startup():
    return 'yes'


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


if __name__ == '__main__':
    window = Window()
    IP = get_host_ip()

    for i in range(30):
        try:
            window.listen('%s://%s:%s/startup' % (SCHEMA, IP, PORT))
            # create service js file
            create_service_js(SCHEMA, IP, PORT)
            # startup server
            run(app=app, host='0.0.0.0', port=PORT)
        except OSError:
            PORT += 1
