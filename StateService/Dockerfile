FROM node:14

# Copy Docker client
COPY --from=docker:latest /usr/local/bin/docker /usr/local/bin/

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose
RUN ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Add application code
ADD rabbitmq-stats.js /
ADD server.js /

# Start server
CMD ["node", "server.js"]