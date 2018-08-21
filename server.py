import glob
import importlib
import inspect
import os
from bottle import request, Bottle, abort, response
from gevent import monkey

monkey.patch_all()

SERVICE = {}
SERVICE_PACKAGE = 'service'
EXT = '.py'
app = Bottle()

files = glob.glob(SERVICE_PACKAGE + '/**', recursive=True)
for f in files:
    if not f.endswith(EXT):
        continue
    module_name = f.replace(os.path.sep, '.')[0:-len(EXT)]
    module = importlib.import_module(module_name)
    keys = module.__dict__.keys()
    # extract Non-private functions
    for key, value in module.__dict__.items():
        if not key.startswith('_') and inspect.isfunction(value):
            service_name = (module_name + '.' + key).replace('.', '/')
            SERVICE[service_name] = value


base_script = r'''
function encodeData(data) {
    if (typeof data === 'object') {
        var r = "";
        for (var c in data) {
            r += c + "=" + encodeURIComponent(data[c]) + "&";
        }
        return r.substring(0, r.length - 1);
    } else {
        return data;
    }
}

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
    var xhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
    success = success || function (data) {
    };
    error = error || function (e) {
        console.error(e)
    };
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
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send(encodeData(data));

}

'''


@app.route('/service.js')
def service():
    global base_script
    script = base_script

    scheme = request.urlparts.scheme
    netloc = request.urlparts.netloc
    for name in SERVICE.keys():
        script += 'initService("%s");\n' % name.replace('/', '.')

    for name, func in SERVICE.items():
        url = '{0}://{1}/{2}'.format(scheme, netloc, name)
        doc = inspect.getdoc(func)
        if doc:
            script += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
        args = inspect.getfullargspec(func).args
        js_args = ', '.join(args)
        if js_args:
            js_args += ', '
        js_args += 'success, error'
        data = '{%s}' % ', '.join(['{0}:{0}'.format(arg) for arg in args])
        script += 'window.%(name)s = function(%(js_args)s){ bindService("%(url)s", %(data)s, success, error); }\n' % {
            "name": name.replace('/', '.'),
            "js_args": js_args,
            "url": url,
            "data": data
        }

    response.headers['Content-Type'] = 'application/javascript'
    return script


@app.route('/<path:path>', method=['GET', 'POST'])
def dispatcher(path):
    params = dict(request.params.decode())
    print(path, params)
    service_function = SERVICE.get(path, None)
    if service_function is None:
        abort(404, 'Service not found!')
    try:
        return service_function(**params)
    except Exception as e:
        abort(500, str(e))


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


app.run(host='0.0.0.0', port=80, server='gevent')
