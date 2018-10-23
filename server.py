import glob
import importlib
import inspect
import json
import os
import random
import sys

from bottle import request, Bottle, response

JS = """
var basePath = "%(base_path)s";
//init service function
function initService(serviceName) {
    var variables = serviceName.split('.');
    var p = window;
    for (var i = 0; i < variables.length; i++) {
        var v = variables[i];
        p[v] = p[v] || {};
        p = p[v];
    }
}

//execute service function
function executeService(serviceName, data, success, error) {
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
                } else {
                    error(r.message);
                }
            } else {
                error(xhr.response);
            }
        }
    }
    xhr.open("POST", basePath + serviceName.replace(/\./g, '/'), true);
    xhr.send(formData);
}
"""


class Service:
    def __init__(self, host='0.0.0.0', port=5000, server='wsgiref', service_package='service', js_route='/service.js'):
        self.app = Bottle()
        self.host = host  # server host
        self.port = port  # server port
        # if server port is None, use a random port
        if self.port is None:
            self.port = random.randint(5000, 10000)
        self.server = server  # wsgi server
        self.service_package = service_package  # service package name
        os.makedirs(self.service_package, exist_ok=True)
        self.js_route = js_route  # route for py service to JS
        self.services = {}  # all service collection
        self.load_service()

    def load_service(self):
        # load service modules and functions
        module_files = glob.glob(self.service_package + '/**.py', recursive=True)
        for module_path in module_files:
            module_name = os.path.splitext(module_path)[0].replace(os.path.sep, '.')
            module = importlib.import_module(module_name)
            # extract Non-private functions as service
            for func_name, func in module.__dict__.items():
                if not func_name.startswith('_') and inspect.isfunction(func):
                    service_name = module_name + '.' + func_name
                    self.services[service_name] = func

        sys.stdout.write('Service loading completed!\n')

    def init_js(self):
        script = JS
        # register service to js
        base_path = '{0}://{1}/'.format(request.urlparts.scheme, request.urlparts.netloc)
        script = script % {'base_path': base_path}
        script += '\n/********************** init service ****************************/\n'
        for service_name in self.services.keys():
            script += 'initService("%s");\n' % service_name
        script += '\n/*********************** execute service ****************************/\n'
        for service_name, service_func in self.services.items():
            # function doc
            doc = inspect.getdoc(service_func)
            if doc:
                script += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
            # function args
            args = inspect.getfullargspec(service_func).args
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

        return script

    def dispatcher(self, path):
        params = dict(request.POST)
        print(path, params)
        service_function = self.services.get(path.replace('/', '.'), None)
        if service_function is None:
            return json.dumps({'code': 404, 'message': 'Service "%s" not found!' % path}, ensure_ascii=False)
        try:
            return json.dumps({'code': 200, 'data': service_function(**params)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'code': 500, 'message': 'Server error: %s' % e}, ensure_ascii=False)

    @staticmethod
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'

    def run(self):
        self.app.route('/<path:path>', method=['POST'], callback=self.dispatcher)
        self.app.route(self.js_route, callback=self.init_js)
        self.app.add_hook('after_request', self.enable_cors)
        self.app.run(host=self.host, port=self.port, server=self.server)


if __name__ == '__main__':
    Service(port=None).run()
