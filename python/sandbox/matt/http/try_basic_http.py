# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

hostName = "localhost"
serverPort = 8001


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        path = self.path[1:]
        if path.find('?') > 0:
            path = path[:path.find('?')]
        cur_dir = os.path.realpath(os.path.join(os.path.realpath(__file__), '..'))
        replied = False
        if len(path) > 0 and os.path.exists(os.path.join(cur_dir, path)) and path.find('..') < 0:
            resource_file = os.path.join(cur_dir, path)
            if os.path.exists(resource_file):
                with open(resource_file, 'r') as f:
                    self.wfile.write(bytes(f.read(), "utf-8"))
                replied = True

        if not replied:
            self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
            self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")