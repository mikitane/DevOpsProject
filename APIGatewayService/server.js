const http = require('http');
const fs = require('fs');

// const LOG_FILE_PATH = '/output/logs.txt';
const port = 8081;
const HTTPSERV_SERVICE_URL = 'http://httpserv_service:8082';
const STATE_SERVICE_URL = 'http://state_service:8083';

const forwardRequest = (req, res, url, method) => {
  http[method](url, forwardRes => {
    forwardRes.on("data", function(forwardMessage) {
      res.statusCode = forwardRes.statusCode;
      res.setHeader('Content-Type', 'text/plain');
      res.end(forwardMessage);
    });
  });
}

const getMessages = (req, res) => {
  forwardRequest(req, res, HTTPSERV_SERVICE_URL, 'get');
}

const getState = (req, res) => {
  forwardRequest(req, res, STATE_SERVICE_URL, 'get');
}

const putState = (req, res) => {
  forwardRequest(req, res, STATE_SERVICE_URL, 'put');
}


const server = http.createServer((req, res) => {
  // if (!fs.existsSync(LOG_FILE_PATH)) return res.end('No content');

  // const content = fs.readFileSync(LOG_FILE_PATH);

  // res.statusCode = 200;
  // res.setHeader('Content-Type', 'text/plain');
  // res.end(content);

  const { method, url, headers } = req

  if (method === "GET" && url === "/messages") {
    return getMessages(req, res);
  };

  if (method === "GET" && url === "/state") {
    return getState(req, res);
  }

  if (method === "PUT" && url === "/state") {
    return putState(req, res);
  }

  res.statusCode = 404
  return res.end('Not found');
});

server.listen(port, () => {
  console.log(`APIGateway running at port ${port}`);
});
