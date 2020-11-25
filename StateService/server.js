const http = require('http');
const fs = require('fs');
const { exec } = require('child_process');

const STATE_FILE_PATH = '/state/state.txt';
const STATE_LOG_FILE_PATH = '/state/state_log.txt';
const MESSAGES_FILE_PATH = '/output/logs.txt';
const PORT = 8083;
const VALID_STATES = ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN'];

const getState = () => {
  return fs.readFileSync(STATE_FILE_PATH);
};

const writeLog = (newState) => {
  const timestamp = new Date().toISOString();
  fs.appendFileSync(STATE_LOG_FILE_PATH, `${timestamp}: ${newState}\n`);
};

const initialize = () => {
  fs.writeFileSync(STATE_FILE_PATH, 'INIT');
  fs.writeFileSync(STATE_LOG_FILE_PATH, '');
  fs.writeFileSync(MESSAGES_FILE_PATH, '');
  writeLog('INIT');
};

const shutdown = () => {
  fs.writeFileSync(STATE_FILE_PATH, 'SHUTDOWN');
  writeLog('SHUTDOWN');

  const projectEnv = process.env.DEVOPS_PROJECT_ENV;
  const nameFilters = {
    prod: 'devops_prod',
    test: 'devops_test',
  };

  const nameFilter = nameFilters[projectEnv];

  exec(
    `docker container stop $(docker container ls -q --filter name=${nameFilter})`,
    (error, stdout, stderr) => {
      if (error) {
        console.log(`error: ${error.message}`);
      }
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
      console.log(`stdout: ${stdout}`);
    }
  );
};

const handleGetState = (req, res) => {
  const state = getState();
  res.statusCode = 200;
  return res.end(state);
};

const handlePutState = (req, res) => {
  const newState = req.data;

  let body = '';
  req.on('data', (chunk) => {
    body += chunk.toString();
  });
  req.on('end', () => {
    const newState = body;

    if (!VALID_STATES.includes(newState)) {
      res.statusCode = 400;
      return res.end('Invalid state!');
    }

    const currentState = getState();

    // No effects if states are same
    if (currentState === newState) {
      res.statusCode = 200;
      return res.end(currentState);
    }

    switch (newState) {
      case 'INIT':
        initialize();
        break;

      case 'SHUTDOWN':
        shutdown();
        break;

      default:
        fs.writeFileSync(STATE_FILE_PATH, newState);
        writeLog(newState);
        break;
    }

    res.statusCode = 200;
    return res.end(newState);
  });
};

const handleGetRunLog = (req, res) => {
  const logs = fs.readFileSync(STATE_LOG_FILE_PATH);
  res.statusCode = 200;
  return res.end(logs);
}

const server = http.createServer((req, res) => {
  const { method, url, headers } = req;

  if (method === 'GET' && url === '/state') {
    return handleGetState(req, res);
  }

  if (method === 'PUT' && url === '/state') {
    return handlePutState(req, res);
  }

  if (method === 'GET' && url === '/run-log') {
    return handleGetRunLog(req, res);
  }
});

initialize();

server.listen(PORT, () => {
  console.log(`StateService running at port ${PORT}`);
});
