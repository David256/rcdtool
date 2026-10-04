SHELL := bash

# docker compose driven workflow
COMPOSE   ?= docker compose
SERVICE   ?= rcdtoold
IMG       ?= rcdtool
NAME      ?= rcdtoold
DATA_DIR  ?= $(CURDIR)/data
# Avoid readonly UID in zsh; use HOST_* and pass as DOCKER_* to compose
HOST_UID  := $(shell id -u 2>/dev/null || echo 1000)
HOST_GID  := $(shell id -g 2>/dev/null || echo 1000)

.PHONY: build up up-nc down ps bash logs restart

build:
	DOCKER_UID=$(HOST_UID) DOCKER_GID=$(HOST_GID) $(COMPOSE) build

up: ## Start long‑lived dev container with volumes
	@mkdir -p "$(DATA_DIR)"
	@if [ ! -f "$(DATA_DIR)/config.ini" ]; then cp -n config.ini.sample "$(DATA_DIR)/config.ini"; fi
	DOCKER_UID=$(HOST_UID) DOCKER_GID=$(HOST_GID) $(COMPOSE) up -d
	@$(COMPOSE) ps

down:
	$(COMPOSE) down

bash:
	$(COMPOSE) exec -w /work $(SERVICE) bash

restart:
	$(COMPOSE) restart $(SERVICE)
