const http = require('http');
const fs = require('fs');

// const LOG_FILE_PATH = '/output/logs.txt';
const PORT = 8081;

const HTTPSERV_SERVICE_HOSTNAME = 'httpserv_service';
const HTTPSERV_SERVICE_PORT = 8082;

const STATE_SERVICE_HOSTNAME = 'state_service';
const STATE_SERVICE_PORT = 8083;

const forwardRequest = (req, res, options, data) => {
  const forwardRequest = http.request(options, (forwardRes) => {
    let forwardData = '';

    forwardRes.on('data', (chunk) => {
      forwardData += chunk.toString();
    });

    forwardRes.on('end', () => {
      res.statusCode = forwardRes.statusCode;
      res.setHeader('Content-Type', 'text/plain');
      res.end(forwardData);
    });
  });

  if (data !== undefined) {
    forwardRequest.write(data);
  }

  forwardRequest.end();
};

const getMessages = (req, res) => {
  const options = {
    hostname: HTTPSERV_SERVICE_HOSTNAME,
    port: HTTPSERV_SERVICE_PORT,
    path: '/',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

const getState = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/state',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

const putState = (req, res) => {
  let data = '';

  req.on('data', (chunk) => {
    data += chunk.toString();
  });

  req.on('end', () => {
    const options = {
      hostname: STATE_SERVICE_HOSTNAME,
      port: STATE_SERVICE_PORT,
      path: '/state',
      method: 'PUT',
    };

    forwardRequest(req, res, options, data);
  });
};

const getRunLog = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/run-log',
    method: 'GET',
  };

  forwardRequest(req, res, options);
}

const getNodeStatistics = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/node-statistic',
    method: 'GET',
  };

  forwardRequest(req, res, options);
}

const getQueueStatistics = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/queue-statistic',
    method: 'GET',
  };

  forwardRequest(req, res, options);
}

const server = http.createServer((req, res) => {
  // if (!fs.existsSync(LOG_FILE_PATH)) return res.end('No content');

  // const content = fs.readFileSync(LOG_FILE_PATH);

  // res.statusCode = 200;
  // res.setHeader('Content-Type', 'text/plain');
  // res.end(content);

  const { method, url, headers } = req;

  if (method === 'GET' && url === '/messages') {
    return getMessages(req, res);
  }

  if (method === 'GET' && url === '/state') {
    return getState(req, res);
  }

  if (method === 'PUT' && url === '/state') {
    return putState(req, res);
  }

  if (method === 'GET' && url === '/run-log') {
    return getRunLog(req, res);
  }

  if (method === 'GET' && url === '/node-statistic') {
    return getNodeStatistics(req, res);
  }

  if (method === 'GET' && url === '/queue-statistic') {
    return getQueueStatistics(req, res);
  }

  res.statusCode = 404;
  return res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`APIGateway running at port ${PORT}`);
});
