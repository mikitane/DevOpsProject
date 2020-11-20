const http = require('http');
const fs = require('fs');

const STATE_FILE_PATH = '/state/state.txt';
const STATE_LOG_FILE_PATH = '/state/state_log.txt';
const PORT = 8083;
const VALID_STATES = ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN']


const getState = () => {
  return fs.readFileSync(STATE_FILE_PATH);
}

const writeLog = newState => {
  const timestamp = (new Date()).toISOString();
  fs.writeFileSync(STATE_LOG_FILE_PATH, `${timestamp}: ${newState}`);
}

const setupFiles = () =>  {
  if (!fs.existsSync(STATE_FILE_PATH)) {
    fs.writeFileSync(STATE_FILE_PATH, 'INIT');
  }

  if (!fs.existsSync(STATE_LOG_FILE_PATH)) {
    fs.writeFileSync(STATE_LOG_FILE_PATH, '');
    writeLog('INIT');
  }
}

const handleGetState = (req, res) => {
  const state = getState();
  res.statusCode = 200;
  return res.end(state);
}

const handlePutState = (req, res) => {
  throw Error("Error")
}

const server = http.createServer((req, res) => {
  const { method, url, headers } = req

  if (method === "GET") {
    return handleGetState(req, res);
  }

  if (method === "PUT") {
    return handlePutState(req, res);
  }
});


setupFiles();

server.listen(PORT, () => {
  console.log(`HttpServ running at port ${PORT}`);
});
