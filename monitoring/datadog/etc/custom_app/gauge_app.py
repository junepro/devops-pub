import http.server
from datadog import initialize, statsd
import time
import random
APP_PORT = 8000

options = {'statsd_host':'localhost',
           'statsd_port':8125}

class HandleRequests(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        start_time = time.time()
        wait_time=random.random()*10
        time.sleep(wait_time)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>First Application</title></head><body style='color: #333; margin-top: 30px;'><center><h2>Welcome to Datadog-Python application.</center></h2></body></html>", "utf-8"))
        end_time = time.time()
        response_time = end_time-start_time
        statsd.gauge('app.request.time', response_time, sample_rate=1, tags =["env:dev" ,"app:pythonapp"])
        
if __name__ == "__main__":
    initialize(**options)
    server = http.server.HTTPServer(('localhost', APP_PORT), HandleRequests)
    server.serve_forever()
