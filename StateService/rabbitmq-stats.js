const http = require('http');

const BROKER_SERVICE_HOSTNAME = 'broker_service';
const BROKER_SERVICE_AUTH = 'guest:guest';
const BROKER_SERVICE_PORT = 15672;

const makeRequest = (customOptions, callback) => {
  const options = {
    hostname: BROKER_SERVICE_HOSTNAME,
    port: BROKER_SERVICE_PORT,
    auth: BROKER_SERVICE_AUTH,
    method: 'GET',
    ...customOptions,
  };

  const rabbitMqReq = http.request(options, (rabbitMqRes) => {
    let rabbitMqData = '';

    rabbitMqRes.on('data', (chunk) => {
      rabbitMqData += chunk.toString();
    });

    rabbitMqRes.on('end', () => {
      callback(rabbitMqData);
    });
  });

  rabbitMqReq.on('error', (err) => {
    callback(null);
  });

  rabbitMqReq.end();
}

const handleGetNodeStatistics = (req, res) => {
  makeRequest({ path: '/api/nodes' }, (data) =>  {
    if (!data) return res.end('{}');

    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');

    try {
      const rabbitMqJson = JSON.parse(data);
      const keys = [
        'fd_used',
        'disk_free',
        'mem_used',
        'processors',
        'io_read_avg_time',
      ];

      const responseData = Object.fromEntries(
        keys.map((key) => [key, rabbitMqJson[0][key]])
      );

      res.end(JSON.stringify(responseData));
    } catch (e) {
      res.end('{}');
    }
  })
};

const handleGetQueueStatistics = (req, res) => {
  console.log('handleGetQueueStatistics 1')
  makeRequest({ path: '/api/queues' }, (data) =>  {
    console.log('handleGetQueueStatistics 2')

    if (!data) return res.end('[]');
    console.log('handleGetQueueStatistics 3')

    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');

    try {
      const rabbitMqJson = JSON.parse(data);

      const responseData = rabbitMqJson.map(queueData => ({
        'queue': queueData.name,
        'message_delivery_rate': queueData.message_stats.deliver_get_details.rate,
        'messages_publishing_rate': queueData.message_stats.publish_details.rate,
        'messages_delivered_recently': queueData.message_stats.deliver_get,
        'message_published_lately': queueData.message_stats.publish,
      }));

      res.end(JSON.stringify(responseData));
    } catch (e) {
      console.log('handleGetQueueStatistics 4')
      console.log(e)
      res.end('[]');
    }
  })
};

module.exports = {
  handleGetNodeStatistics,
  handleGetQueueStatistics,
};
