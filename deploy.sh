#!/bin/sh

# This script is used to deploy the application to
# local or production (remote) environment

# Modify PRODUCTION_* variables to match the
# environment in the production server.
PRODUCTION_USER="devops_deploy"
PRODUCTION_HOST="34.74.12.236"
PRODCUTION_PROJECT_PATH="/home/devops_deploy/DevOpsProject"

# Store your private SSH key in this location
PRODUCTION_SSH_PRIVATE_KEY_FILE="/etc/ssh/devops_deploy_key.txt"

SSH_COMMAND="ssh -o \"StrictHostKeyChecking no\" -i $PRODUCTION_SSH_PRIVATE_KEY_FILE ${PRODUCTION_USER}@${PRODUCTION_HOST}"


if [ "$DEPLOY_ENV" = "prod" ]
then
  echo "Production deployment"
  chmod 600 $PRODUCTION_SSH_PRIVATE_KEY_FILE
  eval $SSH_COMMAND "\"cd $PRODCUTION_PROJECT_PATH; docker-compose down -v\""
  eval $SSH_COMMAND "\"cd $PRODCUTION_PROJECT_PATH; docker-compose up --build --force-recreate -d\""
else
  echo "Local deployment"
  docker-compose down -v
  docker-compose up --build --force-recreate -d
fi
