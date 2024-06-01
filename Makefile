DOCKER_COMPOSE_EXISTS := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")
ifeq ($(DOCKER_COMPOSE_EXISTS),)
	DOCKER_CMD := docker-compose
	DOCKER_COMPOSE_FLAG := 
else
	DOCKER_CMD := docker
	DOCKER_COMPOSE_FLAG := compose
endif

DOCKER_COMPOSE_DEV := $(DOCKER_CMD) $(DOCKER_COMPOSE_FLAG) -f docker/development/docker-compose.yml
DOCKER_COMPOSE_DEBUG_DEV := -f docker/development/docker-compose.override.yml

BUILD_OPTIONS =

# The 'start-development' rule is used to start the development environment.
# This includes building Docker images if necessary, and starting services via Docker Compose.
start-development:
	# Exporting the variables to be used in shell subcommands
	$(eval export BUILD_IMAGE=$(BUILD_IMAGE))
	$(eval export DEBUG=$(DEBUG))
	$(eval export DETACH=$(DETACH))

	# Initialize command with base Docker Compose command
	$(eval export DOCKER_CMD=$(DOCKER_COMPOSE_DEV))

	# In a shell context now, because the variables need to be used in shell if statements.
	# If DEBUG is true, append the debug compose file to the command
	@if [ "$(DEBUG)" = "true" ]; then \
		DOCKER_CMD="$(DOCKER_CMD) $(DOCKER_COMPOSE_DEBUG_DEV)"; \
	fi; \
	# If DETACH is true, append 'up -d' to command for detached mode. \
    # Otherwise, append 'up' for regular mode. \
	if [ "$(DETACH)" = "true" ]; then \
		DOCKER_CMD="$${DOCKER_CMD} up -d"; \
	else \
		DOCKER_CMD="$${DOCKER_CMD} up"; \
	fi; \
	# If BUILD_IMAGE is true, build Docker images before starting services. \
	if [ "$(BUILD_IMAGE)" = "true" ]; then \
		$(DOCKER_COMPOSE_DEV) build $(BUILD_OPTIONS); \
	fi; \
	# Finally, execute the Docker Compose command. \
	$${DOCKER_CMD}

build-development:
	$(DOCKER_COMPOSE_DEV) build


stop-development:
	$(DOCKER_COMPOSE_DEV) stop

create-network:
	docker network create loan_api

help:
	@echo " "
	@echo "Usage: make <command>\n"
	@echo " "
	@echo "Commands:"
	@echo "  start-development     Start development environment."
	@echo "  stop-development      Stop development environment."
	@echo "  create-network        Create Docker network for microservices."
	@echo "  help                  Show available commands, options, examples and tips."
	@echo " "
	@echo "Options for start-development command:"
	@echo "  DEBUG=true            To debug micro service"
	@echo "  BUILD_IMAGE=true      To build Docker image"
	@echo "  BUILD_OPTIONS=<value> Possible values: --no-cache. Applies only if BUILD_IMAGE=true."
	@echo "  DETACH=true           To run docker-compose up with -d"
	@echo " "
	@echo "Examples:"
	@echo "  make start-development                                                       To start development environment"
	@echo "  make start-development DEBUG=true                                            To debug micro service"
	@echo "  make start-development BUILD_IMAGE=true                                      To build Docker image"
	@echo "  make start-development DEBUG=true BUILD_IMAGE=true BUILD_OPTIONS=--no-cache  To debug micro service and build Docker image with --no-cache option"
	@echo "                                                                               Applies only if BUILD_IMAGE=true."
	@echo "  make start-development BUILD_IMAGE=true BUILD_OPTIONS=--no-cache             To build Docker image with --no-cache option"
	@echo "  make start-development DETACH=true                                           To run docker-compose up with -d"
	@echo "  make start-development DEBUG=true DETACH=true                                To debug micro service and run docker-compose up with -d"
	@echo " "
	@echo "Tips:"
	@echo "- It's recommended to run 'make start-development BUILD_IMAGE=true' when a Python dependency is added to requirements.txt."
	@echo "- It's recommended to run 'make start-development BUILD_IMAGE=true BUILD_OPTIONS=--no-cache' when a system dependency is added to the Dockerfile."
	@echo "- If you're developing, you can install system or Python dependencies in the container's without the need to run make start-development"
	@echo "  'BUILD_IMAGE=true' if DEBUG=true is set. However, keep in mind that making changes to the Dockerfile or docker-compose "
	@echo "  file will cause Docker to reload the container and you'll lose any manually installed dependencies."
	@echo " "