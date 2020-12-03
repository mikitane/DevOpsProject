/*
APIGatewayService is the only service that is exposed
to outside networks. This service is responsible for
forwarding the requests from the user to the correct
service.
*/

const http = require('http');
const fs = require('fs');

// Serve requests from this port. This port is
// also accessible from outside networks.
const PORT = 8081;

// HttpServService config
const HTTPSERV_SERVICE_HOSTNAME = 'httpserv_service';
const HTTPSERV_SERVICE_PORT = 8082;

// StateService config
const STATE_SERVICE_HOSTNAME = 'state_service';
const STATE_SERVICE_PORT = 8083;

// Helper function to forward requests to different services
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

// Handler function for /messages GET
// Forwards request to HttpServService
const getMessages = (req, res) => {
  const options = {
    hostname: HTTPSERV_SERVICE_HOSTNAME,
    port: HTTPSERV_SERVICE_PORT,
    path: '/',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

// Handler function for /state GET
// Forwards request to StateService
const getState = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/state',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

// Handler function for /state PUT
// Forwards request to StateService
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

// Handler function for /run-log GET
// Forwards request to StateService
const getRunLog = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/run-log',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

// Handler function for /node-statistic GET
// Forwards request to StateService
const getNodeStatistics = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/node-statistic',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

// Handler function for /queue-statistic GET
// Forwards request to StateService
const getQueueStatistics = (req, res) => {
  const options = {
    hostname: STATE_SERVICE_HOSTNAME,
    port: STATE_SERVICE_PORT,
    path: '/queue-statistic',
    method: 'GET',
  };

  forwardRequest(req, res, options);
};

// Create the server and link urls to correct handlers
const server = http.createServer((req, res) => {
  const { method, url } = req;

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

// Start the server
server.listen(PORT, () => {
  console.log(`APIGateway running at port ${PORT}`);
});
