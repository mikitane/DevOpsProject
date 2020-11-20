const http = require('http');
const fs = require('fs');

// const LOG_FILE_PATH = '/output/logs.txt';
const port = 8081;


const getMessages = (req, res) => {
  http.get("http://httpserv_service:8082", httpservRes => {
    httpservRes.on("data", function(httpservMessage) {
      res.statusCode = httpservRes.statusCode;
      res.setHeader('Content-Type', 'text/plain');
      res.end(httpservMessage);
    });
  });
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

  res.statusCode = 404
  return res.end('Not found');
});

server.listen(port, () => {
  console.log(`APIGateway running at port ${port}`);
});
