import glob
import importlib
import inspect
import json
import os

import yaml
from bottle import request, Bottle, response

# load config
CONFIG = dict(yaml.load(open('config.yml', mode='r', encoding='utf-8')))
SERVER_CONFIG = CONFIG['server-config']
HOST = SERVER_CONFIG.get('host', '0.0.0.0')
PORT = SERVER_CONFIG.get('port', 8888)
SCHEMA = SERVER_CONFIG.get('schema', 'http')
DOMAIN = SERVER_CONFIG.get('domain', 'localhost')
SERVER = SERVER_CONFIG.get('server', 'wsgiref')
SERVICE_PACKAGE = SERVER_CONFIG.get('service-package', 'service')
VIEW_PACKAGE = SERVER_CONFIG.get('view-package', 'view')
SERVICE_JS_PATH = SERVER_CONFIG.get('service-js-path', VIEW_PACKAGE + '/service.js')
SERVICE_JS_TEMPLATE = SERVER_CONFIG.get('service-js-template', '')

app = Bottle()
SERVICE = {}

os.makedirs(SERVICE_PACKAGE, exist_ok=True)
os.makedirs(VIEW_PACKAGE, exist_ok=True)


def init_service():
    # load service modules and functions
    module_files = glob.glob(SERVICE_PACKAGE + '/**.py', recursive=True)
    print(module_files)
    for module_path in module_files:
        module_name = os.path.splitext(module_path)[0].replace(os.path.sep, '.')
        module = importlib.import_module(module_name)
        # extract Non-private functions as service
        for func_name, func in module.__dict__.items():
            if not func_name.startswith('_') and inspect.isfunction(func):
                service_name = module_name + '.' + func_name
                SERVICE[service_name] = func

    print('init service done, service list:', list(SERVICE.keys()))


def create_service_js(scheme, host, port):
    # register service to js
    script = 'var basePath = "{0}://{1}:{2}/";\n'.format(scheme, host, port) + SERVICE_JS_TEMPLATE
    script += '\n/********************** init service ****************************/\n'
    for service_name in SERVICE.keys():
        script += 'initService("%s");\n' % service_name
    script += '\n/*********************** execute service ****************************/\n'
    for service_name, service in SERVICE.items():
        # function doc
        doc = inspect.getdoc(service)
        if doc:
            script += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
        # function args
        args = inspect.getfullargspec(service).args
        data = ', '.join(['{0}: {0}'.format(arg) for arg in args])
        js_args = ', '.join(args + ['success', 'error'])
        # create js service function
        script += 'window.%(service_name)s = function(%(args)s){ executeService("%(service_name)s", {%(data)s}, success, error); }\n' % {
            "service_name": service_name,
            "args": js_args,
            "data": data
        }

    # set Content-Type
    response.headers['Content-Type'] = 'application/javascript'
    # write script to js file
    with open(SERVICE_JS_PATH, mode='w', encoding='utf-8') as file:
        file.write(script)

    print('create service js file done, file path:', SERVICE_JS_PATH)


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
        return json.dumps({'code': 500, 'message': 'Server error: %s' % e}, ensure_ascii=False)


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


def start(port):
    # init service
    init_service()
    # create service js file
    create_service_js(SCHEMA, DOMAIN, port)
    # startup server
    app.run(host=HOST, port=port, server=SERVER)


if __name__ == '__main__':
    start(PORT)
