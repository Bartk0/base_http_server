import unittest

import ddt
import requests
from main import Path, Response


class TestData:
    XML_TEST_DATA = '<?xml version="1.0" encoding="utf-8"?>' \
                    '<status>False</status>' \
                    '<data>' \
                    '<id>FFFF</id>' \
                    '<some_field>some_field_data</some_field>' \
                    '</data>'

    JSON_TEST_DATA = "{test: some_data}"


@ddt.ddt
class TestBaseServer(unittest.TestCase):
    def setUp(self):
        self.url = 'http://0.0.0.0'

    def check_status_and_content_type_json(self, r):
        self.assertEqual(r.status_code, 200)
        self.assertEqual("application/json", r.headers.get("Content-type"))

    def check_status_and_content_type_xml(self, r):
        self.assertEqual(r.status_code, 200)
        self.assertEqual("text/plain", r.headers.get("Content-type"))

    def test_health(self):
        r = requests.get('{}{}'.format(self.url, Path.HEALTH))
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.HEALTH_GOOD_RESPONSE, r.content.decode())

    def test_default_get(self):
        r = requests.get('{}{}'.format(self.url, "/something"))
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.DEFAULT_RESPONSE, r.content.decode())

    @ddt.data(Response.INIT_JSON_DATA, TestData.JSON_TEST_DATA, "")
    def test_default_post(self, value):
        r = requests.post('{}{}'.format(self.url, "/something"), data=value)
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.DEFAULT_RESPONSE, r.content.decode())

    @ddt.data(Response.INIT_JSON_DATA, TestData.JSON_TEST_DATA, "")
    def test_data_post_json(self, value):
        r = requests.post('{}{}'.format(self.url, Path.JSON), data=value)
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())

        r = requests.get('{}{}'.format(self.url, Path.JSON))
        self.check_status_and_content_type_json(r)
        self.assertEqual(value, r.content.decode())

        r = requests.post('{}{}'.format(self.url, Path.JSON), data=Response.GOOD_RESPONSE)
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())

        r = requests.get('{}{}'.format(self.url, Path.JSON))
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())

    @ddt.data(Response.INIT_XML_DATA, TestData.XML_TEST_DATA, "")
    def test_data_post_xml(self, value):
        r = requests.post('{}{}'.format(self.url, Path.XML), data=value)
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())

        r = requests.get('{}{}'.format(self.url, Path.XML))
        self.check_status_and_content_type_xml(r)
        self.assertEqual(value, r.content.decode())

        r = requests.post('{}{}'.format(self.url, Path.XML), data=Response.GOOD_RESPONSE)
        self.check_status_and_content_type_json(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())

        r = requests.get('{}{}'.format(self.url, Path.XML))
        self.check_status_and_content_type_xml(r)
        self.assertEqual(Response.GOOD_RESPONSE, r.content.decode())


if __name__ == "__main__":
    unittest.main()
