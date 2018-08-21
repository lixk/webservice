import glob
import importlib
import inspect
import os

from bottle import request, Bottle, abort,response

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

# print(SERVICE)
# print(*inspect.getfullargspec(SERVICE['service/user/get_user_info']).args)

js_script = r'''
    /**
     * define ajax method
     */
    function encodeData(data) {
        if (typeof data === 'object') {
            var r = "";
            for (var c in data) {
                r += c + "=" + data[c] + "&";
            }
            return r.substring(0, r.length - 1);
        } else {
            return data;
        }
    }

    function trim(s) {
        return s.replace(/^\s+|\s+$/gm, '');
    }

    String.prototype.format = function () {
        if (arguments.length == 0) return this;
        var param = arguments[0];
        var s = this;
        if (typeof(param) == 'object') {
            for (var key in param)
                s = s.replace(new RegExp("\\{" + key + "\\}", "g"), param[key]);
            return s;
        } else {
            for (var i = 0; i < arguments.length; i++)
                s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
            return s;
        }
    }

    function ajaxPost(url, data, success, error) {
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

    function initService(name, args, url) {
        //init service variable
        var variables = name.split('.');
        var p = window;
        for (var i = 0; i < variables.length; i++) {
            var v = variables[i];
            p[v] = p[v] || {};
            p = p[v];
        }
        //init service function
        var data = [];
        if (trim(args)) {
            var argsArray = args.split(',');
            for (var i = 0; i < argsArray.length; i++) {
                var arg = trim(argsArray[i]);
                data.push(arg + ':' + arg);
            }
            args += ', success, error';
        } else {
            args = 'success, error';
        }

        var fun_template = '(window.{name} = function({args}) { ajaxPost("{url}", {data}, success, error) })'.format({
            name: name,
            args: args,
            url: url,
            data: '{' + data.join(', ') + '}'
        });
        eval(fun_template);
    }

'''


@app.route('/service.js')
def service():
    global js_script
    script = js_script

    scheme = request.urlparts.scheme
    netloc = request.urlparts.netloc
    for name, func in SERVICE.items():
        url = '{0}://{1}/{2}'.format(scheme, netloc, name)
        args = ', '.join(inspect.getfullargspec(func).args)
        script += 'initService("{0}", "{1}", "{2}");\n'.format(name.replace('/', '.'), args, url)

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


app.run(host='0.0.0.0', port=80)
