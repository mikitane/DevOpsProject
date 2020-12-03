# COMP.SE.140 Continuous Development and Deployment - DevOps

This is the course project for the course COMP.SE.140 Continuous Development and Deployment - DevOps.
The project consists of a CI/CD pipeline built with Gitlab and a messaging application built with
Docker, Docker Compose, RabbitMQ, node and python.

## Features implemented
- All compulsory features
- /node-statistic -endpoint
- /queue-statistic -endpoint
- Application deployed to external cloud. Application is running in Google Cloud’s Compute Engine. You can access the application from IP: 34.74.12.236


## Instructions for setting up the system

Application was developed and is ensured to work with Ubuntu 20.04.1 LTS virtual machine with memory of 4096 MB and disk space of 40 GB.

It is recommended to use a fresh virtual machine to test the system. You should have Docker and Docker compose installed on this machine. If not, you can install them following these links:
•	Docker: https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script
•	Docker Compose: https://docs.docker.com/compose/install/

Follow these steps to setup the system:
1.	Clone the project from Github: \
`git clone https://github.com/mikitane/DevOpsProject.git`

2.	Go to directory: ./DevOpsProject/GitlabService \
`cd ./DevOpsProject/GitlabService`

3.	Build and start the Gitlab Docker containers \
`docker-compose up --build -d`

4.	Wait for a few minutes for Gitlab services to start

5.	Go to Gitlab Web in your browser (http://localhost:8080). If your virtual machine does not have a browser, the easiest way is to forward the port 8080 with the host machine your virtual machine is running on and use its browser.

6.	Set a password for the root user in Gitlab.

7.	Login in as root user with the password you just set.

8.	In Gitlab, click “New project”

9.	Name the new project “DevOpsProject”

10.	Click “Create project”

11.	In your VM, ensure that you are in the project repository and run following commands: (use credentials created in step 6) \
`git remote add gl-origin http://127.0.0.1/root/devopsproject.git`
`git push -u gl-origin –all`

12.	The project is now pushed to your local Gitlab server. You can inspect the CI/CD pipeline by opening DevOpsProject in Gitlab and by going to CI/CD-page from the sidebar. If everything is set up correctly, the pipeline should be stuck because there is no runner to execute the jobs in the pipeline.

13.	You need a registration token to register the Gitlab Runner with Gitlab Web. In the browser with the project open, go to Settings -> CI/CD -> Runners (Expand) -> Copy the registration token under “Set up a specific Runner manually”

14.	In your VM, run the following script with the registration token you just got. This script registers your Gitlab Runner with Gitlab Web. (Same script is also located in GitlabService/gitlab-runner-register.sh). \

```
docker exec -it gitlab-runner1 \
  gitlab-runner register \
    --non-interactive \
    --registration-token <your-registration-token>\
    --locked=false \
    --description docker-stable \
    --url http://gitlab-web \
    --executor docker \
    --docker-image docker:stable \
    --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
    --docker-volumes "/etc/ssh/devops_deploy_key.txt:/etc/ssh/devops_deploy_key.txt" \
    --docker-network-mode gitlab-network
```

15.	CI/CD-pipeline should now be running and will build, test and deploy the application to the local environment after couple of minutes.

16.	Push new changes to your local Gitlab and CI/CD-pipeline will deploy those changes automatically
git push gl-origin

After following these steps, the production containers are running and APIGatewayService is exposed from the port 8081. You can test the application by requesting the state:
curl localhost:8081/state

If you want to deploy the application to a remote server, you have to follow these steps after your CI/CD pipeline is running.

1.	Create SSH keys. (e.g. with `ssh-keygen`) and store the public key to your remote server. Save the private key to a file located in: `/etc/ssh/devops_deploy_key.txt`

2.	Master branch is setup with local deployment. You can use the branch master_remote which is configured to deploy the application to the remote environment or you can change the DEPLOY_ENV variable in `.gitlab-ci.yml` to remote.

3.	Configure the variables starting with `REMOTE_` in `deploy.sh` -file to match your remote server.

4.	Your remote server should be accessible by ssh and have Docker and Docker Compose installed.

5.	Clone the project from Github to the remote server. The project repository should be located in the same path as indicated by `REMOTE_PROJECT_PATH` variable in `deploy.sh`.

6.	Push changes to your Gitlab server and it should deploy the application to the remote server. \
`git push gl-origin`


## Public API documentation

The application exposes the port 8081 to host machine. This port is used to make requests to APIGatewayService which is responsible for forwarding the requests from the user to the correct internal service and returning the response. \

All compulsory features are served from these endpoints: \
/messages GET \
Returns the messages registered by ObseService. \

/state GET \
Returns the state of the application \

/state PUT \
Takes a new state as a payload and sets application to that state. Possible values are PAUSED, RUNNING, INIT, SHUTDOWN. \

RUNNING = OrigService sends new messages every 3 seconds \
PAUSED = No new messages are sent \
INIT = Initializes the application, all previous data is cleared. Application changes automatically to RUNNING state after a while. \
SHUTDOWN = Stops all the containers that the application uses. \

/run-log GET \
Returns logs of state changes. \
Example log: \
2020-12-03T17:35:43.382Z: INIT \
2020-12-03T17:36:01.260Z: RUNNING \

/node-statistic GET \
Returns statistics of RabbitMQ nodes in JSON format. Response includes following data: \

fd_used = Used file descriptors. \
disk_free = Disk free space in bytes. \
mem_used = Memory used in bytes. \
processors =  Number of cores detected and usable by Erlang. \
io_read_avg_time = Average wall time (milliseconds) for each disk read operation in the last statistics interval. \

/queue-statistic GET \

Returns statistics of RabbitMQ queues in JSON format. Response includes following data: \

queue = Name of the queue \
message_delivery_rate = How much the count of messages delivered has changed per second in the most recent sampling interval. \
messages_publishing_rate = How much the count of messages published has changed per second in the most recent sampling interval. \
messages_delivered_recently = Count of messages delivered \
message_published_lately  = Count of messages published lately \

## Explanation of the main files and directories in the codebase
##### docker-compose.yml and docker-compose.test.yml
There are different docker-compose -files for managing the application in production and testing environment. Separate files were necessary because the test and production containers are executed in the same host machine in the local deployment mode. If these containers would be executed in different machines, only a single file would be needed.

##### .gitlab-ci.yml
This file is used to instruct Gitlab on how to build, test and deploy the application from the CI/CD pipeline.

##### deploy.sh
Helper script for deploying the application to local and remote environments

##### APIGatewayService
This service is the only service that is exposed
to outside networks. This service is responsible for
forwarding the requests from the user to the correct
service.

##### BrokerService
This service is responsible for setting up the RabbitMQ server

##### GitlabService
This service is responsible for setting up the Gitlab Web and Gitlab Runner containers. These containers are managed with separate docker-compose.yml which is located in service’s directory.

##### HttpServService
This service has currently only one responsibility:
reading the message logs produced by ObseService and
sending those back to the client.

##### ImedService
This service is responsible for handling two
different tasks: listening for messages with
my.o routing key and publishing a modified
message with my.i routing key.

##### ObseService
This service is responsible for listening
for messages published with routing key
that matches my.* wild card key.
When message is received it is stored to
the log file

##### OrigService
OrigService is responsible for publishing
new messages every 3 seconds with my.o routing key
The service publishes new messages only when the
application is in RUNNING state

##### StateService
StateService is responsible for managing the state of
the application and statistics from RabbitMQ.
The service serves this data to clients
from HTTP server.
