#    This file is part of WebBox.
#
#    Copyright 2013 Daniel Alexander Smith
#    Copyright 2013 University of Southampton
#
#    WebBox is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with WebBox.  If not, see <http://www.gnu.org/licenses/>.

import urllib, urllib2, logging, cookielib, json, pprint

class WebBoxTests:

    def __init__(self, appid="WebBoxTests"):
        """ Associate command-line test names with test functions. """
        self.tests = {'create_box': self.create_box,
                      'add_data': self.add_data,
                      'list_boxes': self.list_boxes,
                      'get_object_ids': self.get_object_ids,
                      'get_latest': self.get_latest,
                      'query': self.query,
                     }

        self.token = None
        self.appid = appid

        """ Set up a cookies-enabled opener globally. """
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)


    def set_args(self, args):
        """ Move relevant command-line arguments into local variable. """
        self.args = args

        """ Flatten single value lists into flat key/value pair. """
        for key in args:
            if type(args[key]) == type([]) and len(args[key]) == 1:
                args[key] = args[key][0]

        """ Ensure self.server always ends in a / """
        if self.args['server'][-1:] != "/":
            self.args['server'] += "/"


    """ Shared functions. """

    def check_args(self, required):
        not_set = []
        for key in required:
            if key not in self.args or self.args[key] is None or self.args[key] == "":
                not_set.append(key)
        
        if len(not_set) > 0:
            raise Exception("The following values cannot be empty for this test: {0}".format(", ".join(not_set)))

    def get(self, url, values):
        """ Do a GET, decode the result JSON and return it. """
        if values is None:
            values = {}
        if 'box' in self.args:
            values['box'] = self.args['box']
        values['app'] = self.appid

        if self.token is not None:
            values['token'] = self.token

        data = urllib.urlencode(values)
        url += "?" + data

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()

        logging.debug("GET raw results: \n{0}\n".format(the_page))

        status = json.loads(the_page)
        return status

    def put(self, url, values, content_type="application/json"):
        """ Do a PUT, decode the result JSON and return it. """
        if values is None:
            values = {}
        if 'box' in self.args:
            values['box'] = self.args['box']
        values['app'] = self.appid

        if self.token is not None:
            values['token'] = self.token

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        req.add_header("Content-Type", content_type)
        req.get_method = lambda: "PUT"
        response = urllib2.urlopen(req)
        the_page = response.read()

        logging.debug("PUT raw results: \n{0}\n".format(the_page))

        status = json.loads(the_page)
        return status

    def post(self, url, values):
        """ Do a POST, decode the result JSON and return it. """
        if values is None:
            values = {}
        if 'box' in self.args:
            values['box'] = self.args['box']
        values['app'] = self.appid

        if self.token is not None:
            values['token'] = self.token

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()

        logging.debug("POST raw results: \n{0}\n".format(the_page))

        status = json.loads(the_page)
        return status

    def auth(self):
        """ Authenticate to the webbox server. """
        self.check_args(['server','username','password'])
        url = "{0}auth/login".format(self.args['server'])
        values = {"username": self.args['username'], "password": self.args['password']}

        logging.debug("Authentication to URL: {0} with data: {1}".format(url, values))
        status = self.post(url, values)

        if status['code'] != 200:
            raise Exception("Authentication failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            logging.info("Authentication successful.")
    
    def get_token(self):
        """ Get a token for this box. """
        self.check_args(['server','box'])
        url = "{0}auth/get_token".format(self.args['server'])
        values = {"box": self.args['box'], "app": self.appid}

        logging.debug("Get token of box '{0}' to URL: {1}".format(self.args['box'], url))
        status = self.post(url, values)

        if status['code'] != 200:
            raise Exception("Getting a token to box '{0}' failed, response is {1} with code {2}".format(self.args['box'], status['message'], status['code']))
        else:
            self.token = status['token']


    """ Test functions."""

    def create_box(self):
        """ Test to create a box. """
        self.check_args(['server','box'])
        self.auth()

        url = "{0}admin/create_box".format(self.args['server'])
        values = {"name": self.args['box']}

        logging.debug("Creating box: '{0}' on server '{1}'".format(self.args['box'], self.args['server']))
        status = self.post(url, values)

        if not (status['code'] != 200 or status['code'] != 201):
            raise Exception("Box creation failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            logging.info("Creation of box '{0}' successful.".format(self.args['box']))

    def list_boxes(self):
        """ List the boxes on the webbox server. """
        self.check_args(['server'])
        self.auth()

        url = "{0}admin/list_boxes".format(self.args['server'])

        logging.debug("Listing boxes on server '{0}'".format(self.args['server']))
        status = self.get(url, None)

        if status['code'] != 200:
            raise Exception("Listing boxes failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            logging.info("Listing of boxes successful, the boxes are: \n" + "\n".join(status['list']))

    def get_object_ids(self):
        """ Get the IDs of every object in this box. """
        self.check_args(['server', 'box'])
        self.auth()
        self.get_token()

        url = "{0}{1}/get_object_ids".format(self.args['server'], self.args['box'])

        logging.debug("Getting a list of object IDs on server '{0}' in box '{1}'".format(self.args['server'], self.args['box']))
        status = self.get(url, None)

        if status['code'] != 200:
            raise Exception("Listing object IDs failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            logging.info("Listing of objects successful, the object IDs are: \n" + "\n".join(status['uris']))

    def add_data(self):
        """ Test to add data to a box. """
        self.check_args(['server','box','data','version'])
        self.auth()
        self.get_token()

        url = "{0}{1}/".format(self.args['server'], self.args['box'])
        values = {"data": self.args['data'].read(), "version": self.args['version'], "box": self.args['box'], "app": self.appid}

        logging.debug("Adding data to box: '{0}' on server '{1}'".format(self.args['box'], self.args['server']))
        status = self.put(url, values)
        if status['code'] != 201:
            raise Exception("Adding to box {0} failed. Response is {1} with code {2}".format(self.args['box'], status['message'], status['code']))
        else:
            logging.info("Add to box {0} sucessful, new version is: {1}".format(self.args['box'], status['data']['@version']))
            
    def get_latest(self):
        """ Get the latest version of every object in this box. """
        self.check_args(['server', 'box'])
        self.auth()
        self.get_token()

        url = "{0}{1}/get_latest".format(self.args['server'], self.args['box'])

        logging.debug("Getting latest objects on server '{0}' in box '{1}'".format(self.args['server'], self.args['box']))
        status = self.get(url, None)

        if status['code'] != 200:
            raise Exception("Getting latest failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            pretty = pprint.pformat(status['data'], indent=2, width=80)
            logging.info("Getting latest successful, the objects are: \n" + pretty)
            
    def query(self):
        """ Query this box. """
        self.check_args(['server', 'box', 'query'])
        self.auth()
        self.get_token()

        url = "{0}{1}/query".format(self.args['server'], self.args['box'])

        logging.debug("Querying server '{0}' in box '{1}'".format(self.args['server'], self.args['box']))
        status = self.get(url, {'q': self.args['query']})

        if status['code'] != 200:
            raise Exception("Querying failed, response is {0} with code {1}".format(status['message'], status['code']))
        else:
            pretty = pprint.pformat(status['data'], indent=2, width=80)
            logging.info("Querying successful, the objects are: \n" + pretty)

