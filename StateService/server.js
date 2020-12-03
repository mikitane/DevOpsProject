// OrigService is responsible for managing the state of
// the application and statistics from RabbitMQ.
// The service serves this data to clients
// from HTTP server.

const http = require('http');
const fs = require('fs');
const { exec } = require('child_process');
const {
  handleGetNodeStatistics,
  handleGetQueueStatistics,
} = require('./rabbitmq-stats');

// Location of the file that is used to store
// the current state of the application.
const STATE_FILE_PATH = '/state/state.txt';

// Location of the file that is used to store
// changes of the state.
const STATE_LOG_FILE_PATH = '/state/state_log.txt';

// Location of the file that is used to store the logs
// created by ObseService.
const MESSAGES_FILE_PATH = '/output/logs.txt';

// Serve requests from this port. This port is
// accessible only from internal Docker networks
// that this service's container is connected to.
const PORT = 8083;

// Valid states for the application
const VALID_STATES = ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN'];

// Read the current state from file
const getState = () => {
  return fs.readFileSync(STATE_FILE_PATH);
};

// Write a log of state change to file
const writeLog = (newState) => {
  const timestamp = new Date().toISOString();
  fs.appendFileSync(STATE_LOG_FILE_PATH, `${timestamp}: ${newState}\n`);
};

// Sets the application to initial state
// This is used when service is started and
// when state is set to INIT manually
const initialize = () => {
  // Clear all the files that the application uses
  fs.writeFileSync(STATE_FILE_PATH, 'INIT');
  fs.writeFileSync(STATE_LOG_FILE_PATH, '');
  fs.writeFileSync(MESSAGES_FILE_PATH, '');

  writeLog('INIT');
};

// Shuts down all the containers the application
// consists of. Shutdown is started when state
// is set to SHUTDOWN
const shutdown = () => {
  fs.writeFileSync(STATE_FILE_PATH, 'SHUTDOWN');
  writeLog('SHUTDOWN');

  // Names of the containers depend on which
  // environment the application is executed.
  // Possible environments: prod, test
  const projectEnv = process.env.DEVOPS_PROJECT_ENV;
  const nameFilters = {
    prod: 'devops_prod',
    test: 'devops_test',
  };

  const nameFilter = nameFilters[projectEnv];

  // Execute the command to stop the Docker containers
  exec(`docker container stop $(docker container ls -q --filter name=${nameFilter})`);
};

// Handler function for /state GET
// Returns the current state of the application
// to the client.
const handleGetState = (req, res) => {
  const state = getState();
  res.statusCode = 200;
  return res.end(state);
};

// Handler function for /state PUT
// Used to change the state of the application
const handlePutState = (req, res) => {
  let body = '';
  req.on('data', (chunk) => {
    body += chunk.toString();
  });
  req.on('end', () => {
    const newState = body;

    // Ignore invalid states
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

    // Choose correct action to take
    // based on the new value of the state
    // INIT and SHUTDOWN have special handlers
    // RUNNING and PAUSED use the default handler.
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

// Handler function for /run-log GET
// Returns logs of the state changes
const handleGetRunLog = (req, res) => {
  const logs = fs.readFileSync(STATE_LOG_FILE_PATH);
  res.statusCode = 200;
  return res.end(logs);
};

// Create the server and link urls to correct handlers
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

  if (method === 'GET' && url === '/node-statistic') {
    return handleGetNodeStatistics(req, res);
  }

  if (method === 'GET' && url === '/queue-statistic') {
    console.log('server handleGetQueueStatistics')
    return handleGetQueueStatistics(req, res);
  }
});

// Initialize the application's data and state
// when this service is started
initialize();

// Start the server
server.listen(PORT, () => {
  console.log(`StateService running at port ${PORT}`);
});
