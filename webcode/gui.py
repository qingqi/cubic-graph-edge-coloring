"""
This module provides a simple way to build desktop apps using Web technologies.

The idea comes from Onering-Desktop, see http://code.google.com/p/onering-desktop/ .
"""
from PySide import QtNetwork, QtCore

import logging
import os, sys
from cStringIO import StringIO

logger = logging.getLogger(__name__)

class OAppManager(object):
    # singliton
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(OAppManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self._apps = {}

    def register(self, app):
        self._apps[app.name] = app

    def is_register(self, name):
        return name.lower() in self._apps

    def get_app(self, name):
        if self.is_register(name):
            return self._apps[name.lower()]
        raise Exception("This app is not registered")



class WSGIRunner(QtCore.QThread):
    start_response = QtCore.Signal(str, list)
    # cannot str here, str gets converted to unicode
    # it causes problems with binary contents
    write = QtCore.Signal(QtCore.QByteArray)
    wsgi_finished = QtCore.Signal()

    def __init__(self, wsgi_app, method, request, device, reply):
        QtCore.QThread.__init__(self, reply) # set parent to reply
        self.wsgi_app = wsgi_app
        self.method = method
        self.request = request
        self.device = device
        self.reply = reply
        self.prepare_environ()

        # wire the signals
        self.start_response.connect(reply.start_response)
        self.write.connect(reply.write)
        self.wsgi_finished.connect(reply.wsgi_finished)

    def prepare_environ(self):
        request = self.request
        device = self.device
        method = self.method

        environ = {}
        if device is not None:
            http_body = device.readAll().data()
        else:
            http_body = ''
        input = StringIO(http_body)
        environ['wsgi.input'] = input
        environ['wsgi.errors'] = sys.stderr
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True
        environ['wsgi.url_scheme'] = 'oegarn'

        environ['REQUEST_METHOD'] = method
        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = request.url().encodedPath().data()
        environ['QUERY_STRING'] = request.url().encodedQuery().data()
        environ['SERVER_NAME'] = request.url().host()
        environ['SERVER_PORT'] = '80'
        environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
        environ['CONTENT_TYPE'] = request.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
        if environ['CONTENT_TYPE'] is None:
            del environ['CONTENT_TYPE']
        environ['CONTENT_LENGTH'] = request.header(QtNetwork.QNetworkRequest.ContentLengthHeader)
        if environ['CONTENT_LENGTH'] is None:
            del environ['CONTENT_LENGTH']
        for n in request.rawHeaderList():
            name = 'HTTP_%s' % n.data()
            value = request.rawHeader(n)
            environ[name] = value.data()
        self.environ = environ

    def run(self, *args, **kwargs):
        self.headers_set = False
        self.headers_sent = False
        self.response_body = ''

        def write(data):
            if not self.headers_set:
                raise AssertionError("write() before start_response()")
            data = QtCore.QByteArray(data)
            self.write.emit(data)

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if self.headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None     # avoid dangling circular ref
            elif self.headers_set:
                raise AssertionError("Headers already set!")
            self.start_response.emit(status, response_headers)
            self.headers_set = True
            return write

        result = self.wsgi_app(self.environ, start_response)
        try:
            for data in result:
                if data:    # don't send headers until body appears
                    write(data)
                if not self.headers_sent:
                    write('')   # send headers now if body was empty
        finally:
            if hasattr(result, 'close'):
                result.close()
        self.wsgi_finished.emit()


class OApp(QtCore.QObject):
    def __init__(self, name):
        QtCore.QObject.__init__(self)
        self.name = name.lower()
        self._reply = None

    def handle_request(self, method, request, device, parent):
        self._reply = OAppReply(method, request.url(), device, parent)
        return self._reply

class WSGIApp(OApp):
    def __init__(self, name, wsgi_app):
        OApp.__init__(self, name)
        self.wsgi_app = wsgi_app

    def handle_request(self, method, request, device, parent):
        reply = OAppReply(method, request.url(), device, parent)
        runner = WSGIRunner(self.wsgi_app, method, request, device, reply)
        QtCore.QTimer.singleShot(0, runner.start)
        return reply


class OAppReply(QtNetwork.QNetworkReply):
    def __init__(self, method, url, device, parent):
        QtNetwork.QNetworkReply.__init__(self, parent)
        self.method = method
        self.url = url
        self.device = device
        self.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered)
        logger.info('reply created')
        self.content = ''

    @QtCore.Slot(str, list)
    def start_response(self, status, response_headers):
        parts = status.split(' ')
        code = int(parts[0])
        self.setAttribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute, code)
        if len(parts) > 1:
            reason = ' '.join(parts[1:])
            self.setAttribute(QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute, reason)
        for (name, value ) in response_headers:
            logger.info(name)
            logger.info(value)
            self.setRawHeader(name, value)

    @QtCore.Slot(QtCore.QByteArray)
    def write(self, content):
        content = content.data()
        self.content += content

    @QtCore.Slot()
    def wsgi_finished(self):
        logger.info('wsgi_finished')
        self.readyRead.emit()
        self.downloadProgress.emit(len(self.content), len(self.content))
        self.finished.emit()

    def abort(self, *args, **kwargs):
        pass

    def isSequential(self, *args, **kwargs):
        return True

    def bytesAvailable(self):
        return len(self.content) + QtCore.QIODevice.bytesAvailable(self)

    def readData(self, maxlen=0):
        if maxlen < len(self.content):
            result = self.content[:maxlen]
            self.content = self.content[maxlen:]
            return result
        return self.content


class ONetworkAccessManager(QtNetwork.QNetworkAccessManager):
    def __init__(self, parent, manager):
        QtNetwork.QNetworkAccessManager.__init__(self, parent)
        self.setCache(manager.cache())
        self.setCookieJar(manager.cookieJar())
        self.setProxy(manager.proxy())
        self.setProxyFactory(manager.proxyFactory())

        self.methods = {}
        self.methods[QtNetwork.QNetworkAccessManager.HeadOperation] = "HEAD"
        self.methods[QtNetwork.QNetworkAccessManager.GetOperation] = "GET"
        self.methods[QtNetwork.QNetworkAccessManager.PutOperation] = "PUT"
        self.methods[QtNetwork.QNetworkAccessManager.PostOperation] = "POST"

    def createRequest(self, operation, request, device=None):
        app_manager = OAppManager()
        url = request.url()
        logger.info('url %s, scheme %s, host %s', url, url.scheme(), url.host())
        if url.scheme() == 'oegarn' and app_manager.is_register(url.host()):
            app = app_manager.get_app(url.host())
            logger.info('app found')
            reply = app.handle_request(self.methods[operation], request, device, self)
            return reply
        return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, device)
