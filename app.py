import os
import sys
import logging

from PySide import QtCore, QtWebKit, QtGui

from webcode import gui # import gui
from webcode import web
from webcode.js_api import OJSAPI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GraphInspectorApp(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.initialize()

    def initialize(self):
        # create a gui application
        qt_app = QtGui.QApplication(sys.argv)
        self.qt_gui = qt_app 

        # start the web site app and set app manager
        app_manager = gui.OAppManager()     
        app = gui.WSGIApp('core', web.app.wsgi_app) 
        app_manager.register(app)
     
        page = QtWebKit.QWebPage()
        page.setNetworkAccessManager(gui.ONetworkAccessManager( page, page.networkAccessManager()))
        page.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.page = page


        view = QtWebKit.QWebView()
        view.setPage(page)
        view.resize(1024, 950)
        view.move(qt_app.desktop().screen().rect().center() - view.rect().center())
        view.show()
        self.view = view

        
        api = OJSAPI()
        # add to js, then js can access oegarn
        api.attach(self)

    def run(self):
        self.page.mainFrame().load(QtCore.QUrl('oegarn://core/'))
        #self.page.mainFrame().load(QtCore.QUrl('http://www.baidu.com'))
        #self.page.mainFrame().load(QtCore.QUrl('http://keith-wood.name/svg.html'))

        sys.exit(self.qt_gui.exec_())


app = GraphInspectorApp()
app.run()
