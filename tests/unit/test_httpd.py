import unittest
from unittest.mock import Mock
import io
import os
import logging
from tests.helpers import cases
import socket
import httpd


class SockReadMock:

    def __init__(self, content):
        self.content = bytes(content, encoding='utf-8')
        self.length = len(self.content)
        self.pointer = 0

    def recv(self, chunk_size):
        _chunk_size = min(self.length - self.pointer, chunk_size)
        chunk = self.content[self.pointer:(self.pointer+_chunk_size)]
        self.pointer += _chunk_size
        return chunk


class SockWriteMock:

    def __init__(self):
        self.content = None
        self.file = None

    def sendall(self, content):
        self.content = content

    def sendfile(self, file):
        self.file = file


class TestFileContentLength(unittest.TestCase):

    TEST_LOG_DIR = 'tests_unit'

    def setUp(self):
        os.mkdir(self.TEST_LOG_DIR)

    def tearDown(self):
        for filename in os.listdir(self.TEST_LOG_DIR):
            os.remove(os.path.join(self.TEST_LOG_DIR, filename))
        os.rmdir(self.TEST_LOG_DIR)

    @cases([
        '123',
        'foobar',
        '',
    ])
    def test_file_content_length_bytes_io_valid(self, content):
        bytes_content = bytes(content, encoding='utf-8')
        content_length = len(bytes_content)
        fd = io.BytesIO(bytes_content)
        self.assertEqual(content_length, httpd.file_content_length(fd))

    @cases([
        '123',
        'foobar',
        '',
    ])
    def test_file_content_length_valid(self, content):
        bytes_content = bytes(content, encoding='utf-8')
        content_length = len(bytes_content)

        filepath = os.path.join(self.TEST_LOG_DIR, 'f.txt')
        with io.open(filepath, 'wb') as fr:
            fr.write(bytes_content)

        with io.open(filepath, 'rb') as fd:
            self.assertEqual(content_length, httpd.file_content_length(fd))


class TestSocketReadData(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @cases([
        'foobar',
        ''
    ])
    def test_socket_read_data_ok(self, content):
        content += '\r\n\r\n'
        bytes_content = bytes(content, encoding='utf-8')
        sock = Mock(
            recv=Mock(return_value=bytes_content)
        )
        self.assertEqual(bytes_content, httpd.socket_read_data(sock, 0, 0))

    @cases([
        'foobar',
        '0123456789',
        ''
    ])
    def test_socket_read_data_by_chunk_ok(self, content):
        content += '\r\n\r\n'
        sock_mock = SockReadMock(content)
        sock = Mock(
            recv=sock_mock.recv
        )
        self.assertEqual(sock_mock.content, httpd.socket_read_data(sock, 1, 2 * len(sock_mock.content)))

    @cases([
        'foobar',
        '0123456789'
    ])
    def test_socket_read_data_max_size_ok(self, content):
        content += '\r\n\r\n'
        sock_mock = SockReadMock(content)
        sock = Mock(
            recv=sock_mock.recv
        )
        self.assertEqual(sock_mock.content[0:2], httpd.socket_read_data(sock, 2, 1))

    def test_socket_read_data_timeout_ok(self):
        sock = Mock(
            recv=Mock(side_effect=socket.timeout),
            gettimeout=Mock(return_value=42)
        )
        self.assertEqual(b"", httpd.socket_read_data(sock, 0, 0))


class TestHttpRequest(unittest.TestCase):

    def test_http_request_from_raw(self):

        method = 'GET'
        path = '/foobar'
        version = 'HTTP/1.1'

        headers = [
            'foo: bar',
            'foobar: foobar',
            'x: y'
        ]

        line = '%s %s %s' % (method, path, version)
        line += '\r\n'
        line += "\r\n".join(headers)
        line += "\r\n"

        bytes_line = bytes(line, encoding='utf-8')

        request = httpd.HTTPRequest.from_raw(bytes_line, encoding='utf-8')

        self.assertEqual(method, request.method)
        self.assertEqual(path, request.path)
        self.assertEqual(version, request.version)
        self.assertEqual(sorted(headers), sorted(request.headers))
        self.assertEqual(None, request.body)


class TestHttpResponse(unittest.TestCase):

    def test_http_response_has_must_have_headers(self):
        response = httpd.HTTPResponse(status='status', headers=['foo:bar'], encoding='utf-8')
        sock_mock = SockWriteMock()
        sock = Mock(
            sendall=sock_mock.sendall,
            sendfile=sock_mock.sendfile
        )
        response.send(sock)

        must_have_headers = [
            'Server',
            'Connection',
            'Date',
            'Content-Length'
        ]

        for header in must_have_headers:
            with self.subTest(name=header):
                self.assertIn(
                    bytes('%s: ' % header, encoding='utf8'),
                    sock_mock.content
                )








