import argparse
import inspect
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps


class Path:
    JSON = "/json"
    XML = "/xml"
    HEALTH = "/health"

    @staticmethod
    def get_paths():
        return [attr_pair[1] for attr_pair in
                inspect.getmembers(Path, lambda attr_name: not (inspect.isroutine(attr_name))) if
                not (attr_pair[0].startswith('__') and attr_pair[0].endswith('__'))]


class Response:
    HEALTH_GOOD_RESPONSE = dumps({"message": "I'm doing great!"})
    DEFAULT_RESPONSE = dumps({"message": "Hello there. This is a default server response. Try valid URLs: {0}".format(
        Path.get_paths())})
    GOOD_RESPONSE = dumps({"message": "I got your data"})
    INIT_JSON_DATA = dumps({"status": True, "data": {"id": "FEFE", "some_field": "some_field_data"}})
    INIT_XML_DATA = '<?xml version="1.0" encoding="utf-8"?>' \
                    '<status>True</status>' \
                    '<data>' \
                    '<id>FEFE</id>' \
                    '<some_field>some_field_data</some_field>' \
                    '</data>'


class Storage:
    def __init__(self):
        self.json = Response.INIT_JSON_DATA
        self.xml = Response.INIT_XML_DATA

    def write_json(self, data):
        self.json = data

    def read_json(self):
        return self.json

    def write_xml(self, data):
        self.xml = data

    def read_xml(self):
        return self.xml


class Server(HTTPServer):
    def __init__(self, address, request_handler, storage, paths, response):
        super().__init__(address, request_handler)
        self.storage = storage
        self.path = paths
        self.response = response


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        self.response_json_data = server_class.storage.read_json()
        self.response_xml_data = server_class.storage.read_xml()
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        if self.path == self.server_class.path.JSON:
            return self.json_response()

        if self.path == self.server_class.path.XML:
            return self.xml_response()

        if self.path == self.server_class.path.HEALTH:
            return self.return_health()

        return self.default_response()

    def do_POST(self):
        if self.path == self.server_class.path.JSON:
            return self.store_json_test_data()

        if self.path == self.server_class.path.XML:
            return self.store_xml_test_data()

        return self.default_response()

    def set_json_headers(self, success_response=None):
        self.send_response(200)
        if success_response is not None:
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", str(len(success_response)))
        self.end_headers()

    def set_xml_headers(self, success_response=None):
        self.send_response(200)
        if success_response is not None:
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-Length", str(len(success_response)))
        self.end_headers()

    def set_response(self, response):
        self.wfile.write(str(response).encode('utf8'))

    def json_response(self):
        """
        Response with test data stored in runtime.
        """
        self.set_json_headers(self.response_json_data)
        self.set_response(self.response_json_data)

    def xml_response(self):
        """
        Response with test data stored in runtime.
        """
        self.set_xml_headers(self.response_xml_data)
        self.set_response(self.response_xml_data)

    def store_json_test_data(self):
        """
        Store test data in runtime. Use it for uploading new one.
        """
        success_response = self.server_class.response.GOOD_RESPONSE
        self.set_json_headers(success_response)
        self.set_response(success_response)

        if self.headers.get('Content-Length') is not None:
            self.server_class.storage.write_json(self.rfile.read(int(self.headers['Content-Length'])).decode())

    def store_xml_test_data(self):
        """
        Store test data in runtime. Use it for uploading new one.
        """
        success_response = self.server_class.response.GOOD_RESPONSE
        self.set_json_headers(success_response)
        self.set_response(success_response)

        if self.headers.get('Content-Length') is not None:
            self.server_class.storage.write_xml(self.rfile.read(int(self.headers['Content-Length'])).decode())

    def return_health(self):
        """
        Implementation for health method and response.
        """
        self.set_json_headers(self.server_class.response.HEALTH_GOOD_RESPONSE)
        self.set_response(self.server_class.response.HEALTH_GOOD_RESPONSE)

    def default_response(self):
        """
        Implementation for default server response.
        """
        self.set_json_headers(self.server_class.response.DEFAULT_RESPONSE)
        self.set_response(self.server_class.response.DEFAULT_RESPONSE)


def run(addr, port, server_class=Server, handler_class=RequestHandler):
    server_address = (addr, port)
    http_server = server_class(server_address, handler_class, Storage(), Path, Response)
    print(f"Starting server on {addr}:{port}")
    http_server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Run a simple HTTP server. List of available paths: {0}".format(
        Path.get_paths()))
    parser.add_argument(
        "-l",
        "--listen",
        default="0.0.0.0",
        help="Specify the IP address which server should listen",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=80,
        help="Specify the port which server should listen",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)


if __name__ == "__main__":
    main()
