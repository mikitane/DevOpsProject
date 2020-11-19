#!/bin/sh
# Get the registration token from:
# http://localhost:8080/root/${project}/settings/ci_cd

registration_token=XXXXXXXXXXXXXXXXX

docker exec -it gitlab-runner2 \
  gitlab-runner register \
    --non-interactive \
    --registration-token ${registration_token} \
    --locked=false \
    --description docker-stable \
    --url http://gitlab-web \
    --executor docker \
    --docker-image docker:stable \
    --docker-network-mode gitlab-network
