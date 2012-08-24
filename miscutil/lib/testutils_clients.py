## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Test client and request factory for creating request mock objects.

Classes in this module relies heavily on Werkzeug's test utilities to
do the heavy lifting. For further details please see 
http://werkzeug.pocoo.org/docs/test/.

Which method to use?
  * TestClient: Loads the Invenio WSGI application, and passes requests
    to the application. Works likes a browser, and have support for cookies etc.
  * RequestFactory: Generates a request mock object which you can manually
    pass into a view function in your WebInterface. This way you bypass the
    entire WSGI application - on the other hand it does not support cookies etc. 
"""

from invenio.webinterface_handler_wsgi import SimulatedModPythonRequest
from werkzeug.test import Client, EnvironBuilder
from werkzeug.wrappers import BaseResponse
import json

class RequestFactory(object):
    """
    Factory for creating request mock objects which can be passed to 
    views for testing. 
    
    Example usage::
      pages = WebInterfaceSomePages()
    
      rf = RequestFactory()
      req = rf.post("/deposit/ajaxgateway", data={'key':'value'})
      res = pages.index(req, req.form)
      
    The RequestFactory is relying on Werkzeug's EnvironBuilder to 
    generate an WSGI environment. 
    
    Please see http://werkzeug.pocoo.org/docs/test/#werkzeug.test.EnvironBuilder
    for further details about which arguments are possible to pass into `extras`
    and `request` parameters.
    """
    def __init__(self, **defaults):
        """
        @param defaults: Default parameters to EnvironBuilder.
        """
        self.defaults = defaults
    
    def _start_response(self, *args, **kwargs):
        # Do nothing. Needed for SimulatedModPythonRequest
        pass
    
    def request(self, **request):
        """
        Create a request object. Used by get and post methods.
        
        @return: SimulatedModPythonRequest
        """
        base = {}
        base.update(self.defaults)
        base.update(request)
        
        env = EnvironBuilder(**base)
        return SimulatedModPythonRequest(env.get_environ(), self._start_response)
        
    def get(self, path, data={}, **extras):
        """
        Create a GET request
        
        @return: SimulatedModPythonRequest
        """
        request = {}
        request.update(extras)
        request.update({ 'method' : 'GET', 'query_string': data, 'path': path, 'data': {} })
        return self.request(**request)
    
    def post(self, path, data={}, **extras):
        """
        Create a POST request
        
        @return: SimulatedModPythonRequest
        """
        request = {}
        request.update(extras)
        request.update({ 'method' : 'POST', 'data': data, 'path': path })
        return self.request(**request)


class TestClient(Client):
    """
    Convenience class around Werkzeug's test client.
    
    Main differences is that the WSGI application is already set, 
    as well as methods for performing login/logout.
    
    Please see http://werkzeug.pocoo.org/docs/test/#werkzeug.test.Client for
    further details.
    
    Example usage::
      client = TestClient()
      client.login('admin','')
      response = client.get("/deposit", query_string={'ln':'en'})
      
      assert(response.status_code == 200)
      print response.data
      
      response = client.post(
          "/deposit",
          query_string={'ln':'en',}, # GET parameters
          data={
            'somefile': (StringIO("Text in textfile"), 'filename.txt'),
            'somekey' : 'somevalue'
          }, # POST parameters
      )
      
    """
    def __init__(self, **kwargs):
        from invenio.webinterface_handler_wsgi import application
        defaults = {
            'response_wrapper' : BaseResponse,
        }
        defaults.update(kwargs)
        super(TestClient, self).__init__(application, **defaults)
        
    def login(self, username, password):
        """
        Invenio login
        """
        data = {
            'login_method' : 'Local',
            'ln' : 'en',
            'referer' : '',
            'p_un' : username,
            'p_pw' : password,
            'remember_me' : '',
            'action' : 'login'
        }
        return self.post('/youraccount/login', data=data)
    
    def logout(self):
        """
        Invenio logout
        """
        return self.get('/youraccount/logout')


class JSONResponse(BaseResponse):
    """
    Reponse class for use with TestClient which will decode JSON responses
    from the TestClient. The decoded response is available in the 
    property 'json'::
    
      client = TestClient(response_wrapper=JSONResponse)
      resp = client.get(...)
      resp.json['somekey']
    """
    
    def _get_json(self):
        """
        Decoded JSON response.  
        """
        return json.loads(self.data)

    def _set_json(self, value):
        self.data = json.dumps(value)
    json = property(_get_json, _set_json, doc=_get_json.__doc__)
    del _get_json, _set_json