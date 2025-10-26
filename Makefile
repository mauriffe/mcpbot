COMPOSE_FILE := docker-compose.yml

.PHONY: build
# Builds or rebuilds all service images (app and client).
build:
	@echo "Building all service images..."
	docker-compose -f $(COMPOSE_FILE) build

.PHONY: start-server
# Starts only the long-running server container in detached mode.
start-server:
	@echo "Starting server (mcpserver) in detached mode..."
	docker-compose -f $(COMPOSE_FILE) up -d mcpserver

.PHONY: start-client
# Starts only the long-running server container in detached mode.
start-client:
	@echo "Starting server (mcpserver) in detached mode..."
	docker-compose -f $(COMPOSE_FILE) up -d client

.PHONY: stop
# Stop running services without removing their containers.
stop:
	@echo "Stopping running services..."
	docker-compose -f $(COMPOSE_FILE) stop

.PHONY: down
# Stop and remove all containers, networks, and volumes defined in the compose file.
down:
	@echo "Stopping and removing all containers, networks, and volumes..."
	docker-compose -f $(COMPOSE_FILE) down -v

# --- Client and Utility Targets ---

.PHONY: logs
# View combined logs for all running services (press Ctrl+C to exit).
logs:
	@echo "Viewing service logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: clean
# Alias for 'down'.
clean: down

# Remove all images for this project
.PHONY: clean-images
clean-images:
	@echo "Removing Docker images for this project..."
	docker-compose -f $(COMPOSE_FILE) down --rmi all
	@echo "Images removed successfully"

# --- Combined/Convenience Target ---

.PHONY: setup-and-go
# Builds all images, starts the server, and then launches the client shell.
setup-and-go: build start-server start-client
	@echo "MCP Server and Gemini Client are running."

.PHONY: clean-all
# Remove containers and remove images
clean-all: clean clean-images
	@echo "Images and containers removed"

.PHONY: help
# Display available commands.
help:
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Core Commands:"
	@echo "  build         : Builds (or rebuilds) all service images."
	@echo "  start-server  : Starts the long-running server (mcpserver) container in detached mode."
	@echo "  start-client  : Starts the long-running client (client) container in detached mode."
	@echo "  stop          : Stops running containers."
	@echo "  down / clean  : Stops and removes all containers, networks, and volumes."
	@echo ""
	@echo "Utility Commands:"
	@echo "  logs            : View combined logs of all running services."
	@echo "  clean-images    : Remove all images for this project."
	@echo ""
	@echo "Combined Commands:"
	@echo "  setup-and-go  : [build] -> [start-server] -> [shell-client]"
	@echo "  clean-all  : [clean] -> [clean-images]"
	@echo ""