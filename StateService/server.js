const http = require('http');
const fs = require('fs');

const STATE_FILE_PATH = '/state/state.txt';
const STATE_LOG_FILE_PATH = '/state/state_log.txt';
const MESSAGES_FILE_PATH = '/output/logs.txt';
const PORT = 8083;
const VALID_STATES = ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN']


const getState = () => {
  return fs.readFileSync(STATE_FILE_PATH);
}

const writeLog = newState => {
  const timestamp = (new Date()).toISOString();
  fs.writeFileSync(STATE_LOG_FILE_PATH, `${timestamp}: ${newState}`);
}

const initialize = () =>  {
  fs.writeFileSync(STATE_FILE_PATH, 'INIT');
  fs.writeFileSync(STATE_LOG_FILE_PATH, '');
  fs.writeFileSync(MESSAGES_FILE_PATH, '');
  writeLog('INIT');

  // if (!fs.existsSync(STATE_FILE_PATH)) {
  // }

  // if (!fs.existsSync(STATE_LOG_FILE_PATH)) {

  // }
}

const handleGetState = (req, res) => {
  const state = getState();
  res.statusCode = 200;
  return res.end(state);
}

const handleInitState = () => {

}

const handlePutState = (req, res) => {
  const newState = req.data;

  let body = '';
  req.on('data', chunk => {
      body += chunk.toString();
  });
  req.on('end', () => {
      const newState = body;

      if (!VALID_STATES.includes(newState)) {
        res.statusCode = 400;
        return res.end('Invalid state!')
      }

      const currentState = getState();

      // No effects if states are same
      if (currentState === newState) {
        res.statusCode = 200;
        return res.end(currentState);
      }

      if (newState === 'INIT') {
        initialize();
      } else {
        fs.writeFileSync(STATE_FILE_PATH, newState);
        writeLog(newState);
      }

      res.statusCode = 200;
      return res.end(newState);
  });
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


initialize();

server.listen(PORT, () => {
  console.log(`HttpServ running at port ${PORT}`);
});
