# Copyright (c) 2020, Jeremy Lin
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys, os

PYTHON_BIN = "/usr/bin/python3"
if sys.executable != PYTHON_BIN:
    os.execl(PYTHON_BIN, PYTHON_BIN, *sys.argv)

import webob     # https://pypi.org/project/WebOb/
import wsgiproxy # https://pypi.org/project/WSGIProxy2/

# Change this if you cloned the repo into a non-default directory.
BITWARDENRS_HOME = "{}/{}".format(os.getenv("HOME"), "bwrs")

def getenv(key, default):
    env_file = "{}/{}".format(BITWARDENRS_HOME, "env.sh")
    with open(env_file, "r") as f:
        for ln in f:
            ln = ln.strip()
            if len(ln) == 0 or ln.startswith("#"):
                # Skip blank/commented lines.
                continue
            toks = ln.split("=")
            if len(toks) == 2:
                # We're only looking for lines of the form KEY=VAL.
                if key == toks[0].strip():
                    return toks[1].strip()
        return default

BACKEND_HOST = getenv("ROCKET_ADDRESS", "localhost")
BACKEND_PORT = getenv("ROCKET_PORT", 28973)

HTTP_PREFIX = "http://"
HTTPS_PREFIX = "https://"
BACKEND_URL = "http://{}:{}".format(BACKEND_HOST, BACKEND_PORT)
PROXY = wsgiproxy.HostProxy(BACKEND_URL)

def application(environ, start_response):
    req = webob.Request(environ)

    if req.url.startswith(HTTP_PREFIX):
        # Redirect HTTP to HTTPS.
        https_url = HTTPS_PREFIX + req.url[len(HTTP_PREFIX):]
        res = webob.exc.HTTPMovedPermanently(location=https_url)
    else:
        # Proxy the request to the backend.
        res = req.get_response(PROXY)

    start_response(res.status, res.headerlist)
    return [res.body]
