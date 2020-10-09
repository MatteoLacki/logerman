from urllib.request import Request, urlopen
from urllib.error import URLError
import json
from pathlib import Path
import socket

from .json_ops import dump2json
from .db import LOG


class Sender(object):
    def __init__(self,
                 name,
                 host,
                 port=8745, 
                 encoding="cp1251"):
        self.host = host
        self.port = port
        self.encoding = encoding
        self.name = name
        self.ip = socket.gethostbyname(socket.gethostname())
        self.project_id = self.__get_project_id()
        self.group = name


    def __sock(self, route, message=None):
        url = f"http://{self.host}:{self.port}/{route}"
        request = Request(url)
        request.add_header('Content-Type', 'application/json; charset=utf-8')
        if message is None:
            message = json.dumps(self.name).encode(self.encoding)
        return urlopen(request, message)


    def __get_project_id(self):
        with self.__sock('get_project_id') as s:
            return json.loads(s.read())


    def log(self, key, value):
        """Log key-value.
        
        Args:
            key (str): Parameter name.
            value (obj): Any serializable object.

        Returns:
            boolean: success?
        """
        _log = json.dumps((self.ip, 
                           self.project_id,
                           self.name,
                           self.group,
                           key, 
                           dump2json(value))).encode(self.encoding)
        with self.__sock('log', _log) as s:
            return json.loads(s.read())            


    def update_group(self, group):
        self.group = dump2json(group) # general.


    def list_logs(self):
        with self.__sock('get_all_logs') as s:
            return [LOG(*log) for log in json.loads(s.read())]



class MockSender():
    def log(self, *args, **kwds):
        pass

    def update_group(self, *args, **kwds):
        pass


if __name__ == '__main__':
    s = Sender('Test')
    print(s.project_id)
    print(s.all_logs_df())