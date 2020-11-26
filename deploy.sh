#!/bin/sh


PRODUCTION_USER="devops_deploy"
PRODUCTION_HOST="34.74.12.236"
PRODUCTION_SSH_PRIVATE_KEY_FILE="deploy_key.txt"
PRODCUTION_PROJECT_PATH="/home/devops_deploy/DevOpsProject"

SSH_COMMAND="ssh -o \"StrictHostKeyChecking no\" -i $PRODUCTION_SSH_PRIVATE_KEY_FILE ${PRODUCTION_USER}@${PRODUCTION_HOST}"


if [ "$DEPLOY_ENV" = "prod" ]
then
  ls -l
  pwd
  echo "Production deployment"
  chmod 600 $PRODUCTION_SSH_PRIVATE_KEY_FILE
  eval $SSH_COMMAND "\"cd $PRODCUTION_PROJECT_PATH; docker-compose down -v\""
  eval $SSH_COMMAND "\"cd $PRODCUTION_PROJECT_PATH; docker-compose up --build --force-recreate -d\""
else
  echo "Local deployment"
  docker-compose down -v
  docker-compose up --build --force-recreate -d
fi
