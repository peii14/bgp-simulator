# BGP Protocol Simulator

## Overview

This project simulates BGP (Border Gateway Protocol) routing using Docker containers. Each router is represented as a separate Docker container.

## Prerequisites

Docker

## Getting Started

### Building the Docker Images

To build the Docker images for the BGP routers, use the following command:

```bash
docker-compose build
```

This will create Docker images based on the Dockerfile provided in each service directory.

### Starting the Containers

Once the images are built, you can start the containers using:

```bash
docker-compose up
```
### Stopping the Containers

To stop the running containers, use:

```bash
docker-compose down
```

This will stop and remove the containers, networks, and volumes defined in the docker-compose.yml file.

Configuration

You can configure each router by modifying the respective configuration files in the configs directory. Make sure to update the docker-compose.yml if you add new services or change the configuration.


## TO DO:
- [ ] Routing table:
    - [ ] once a router is dead changing the routing table
    - [ ] Listening for a new connection from other router
- [ ] Define the BGP protocol processing and functionality for the router
- [ ] Simulate error conditions
- [ ] Create Architecture Diagrams
- [ ] Create timestamp for logging
- [ ] error handling
