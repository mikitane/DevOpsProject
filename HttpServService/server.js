/*
HttpServService has currently only one responsibility:
reading the message logs produced by ObseService and
sending those back to the client.
*/

const http = require('http');
const fs = require('fs');

// Location of the file that is used to store the logs
// created by ObseService.
const LOG_FILE_PATH = '/output/logs.txt';

// Serve requests from this port. This port is
// accessible only from internal Docker networks
// that this service's container is connected to.
const port = 8082;

// Create server and setup handler for requests.
// TODO: Separate the request handling to own function.
const server = http.createServer((req, res) => {
  if (!fs.existsSync(LOG_FILE_PATH)) return res.end('');

  const content = fs.readFileSync(LOG_FILE_PATH);

  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end(content);
});

// Start the server
server.listen(port, () => {
  console.log(`HttpServ running at port ${port}`);
});
