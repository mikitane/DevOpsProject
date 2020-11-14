const http = require('http');
const fs = require('fs');

const LOG_FILE_PATH = '/output/logs.txt';
const port = 8080;

const server = http.createServer((req, res) => {
  if (!fs.existsSync(LOG_FILE_PATH)) return res.end('No content');

  const content = fs.readFileSync(LOG_FILE_PATH);

  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end(content);
});

server.listen(port, () => {
  console.log(`HttpServ running at port ${port}`);
});
