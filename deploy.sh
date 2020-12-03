#!/bin/sh

# This script is used to deploy the application to
# local or production (remote) environment

# Modify REMOTE_* variables to match the
# environment in the remote server.
REMOTE_USER="devops_deploy"
REMOTE_HOST="34.74.12.236"
REMOTE_PROJECT_PATH="/home/devops_deploy/DevOpsProject"

# Store your private SSH key for the remote server in this location
REMOTE_SSH_PRIVATE_KEY_FILE="/etc/ssh/devops_deploy_key.txt"

SSH_COMMAND="ssh -o \"StrictHostKeyChecking no\" -i $REMOTE_SSH_PRIVATE_KEY_FILE ${REMOTE_USER}@${REMOTE_HOST}"


if [ "$DEPLOY_ENV" = "remote" ]
then
  echo "Production deployment"
  chmod 600 $REMOTE_SSH_PRIVATE_KEY_FILE



  eval $SSH_COMMAND "\"cd $REMOTE_PROJECT_PATH; git pull origin"
  eval $SSH_COMMAND "\"cd $REMOTE_PROJECT_PATH; git checkout $CI_COMMIT_BRANCH"
  eval $SSH_COMMAND "\"cd $REMOTE_PROJECT_PATH; git pull origin $CI_COMMIT_BRANCH"
  eval $SSH_COMMAND "\"cd $REMOTE_PROJECT_PATH; docker-compose down -v\""
  eval $SSH_COMMAND "\"cd $REMOTE_PROJECT_PATH; docker-compose up --build --force-recreate -d\""
else
  echo "Local deployment"
  docker-compose down -v
  docker-compose up --build --force-recreate -d
fi
