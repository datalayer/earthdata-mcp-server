# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

SHELL=/bin/bash

.DEFAULT_GOAL := default

.PHONY: clean build test lint release

# The package version, read from the one place it is written.
VERSION = $(shell python -c "import re;print(re.search(r'__version__ = \"(.+)\"', open('earthdata_mcp_server/__version__.py').read())[1])")

default: all ## Default target is all.

help: ## display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: clean dev ## Clean Install and Build

install:
	pip install .

dev:
	pip install -e ".[test,lint,typing]"

test: ## run the tests
	pytest -q

lint: ## ruff and mypy, as CI runs them
	ruff check earthdata_mcp_server
	mypy earthdata_mcp_server

build:
	pip install build
	python -m build .

clean: ## clean
	git clean -fdx

build-docker:
	docker buildx build --platform linux/amd64,linux/arm64 -t datalayer/earthdata-mcp-server:${VERSION} .
	docker image tag datalayer/earthdata-mcp-server:${VERSION} datalayer/earthdata-mcp-server:latest

push-docker:
	docker push datalayer/earthdata-mcp-server:${VERSION}
	docker push datalayer/earthdata-mcp-server:latest

pull-docker:
	docker pull datalayer/earthdata-mcp-server:latest

claude-linux:
	NIXPKGS_ALLOW_UNFREE=1 nix run github:k3d3/claude-desktop-linux-flake \
		--impure \
		--extra-experimental-features flakes \
		--extra-experimental-features nix-command

jupyterlab:
	pip uninstall -y pycrdt datalayer_pycrdt
	pip install datalayer_pycrdt
	jupyter lab \
		--port 8888 \
		--ip 0.0.0.0 \
		--ServerApp.root_dir ./dev/content \
		--IdentityProvider.token MY_TOKEN

start: ## start the earthdata mcp server with streamable-http transport
	@exec echo
	@exec echo MCP server endpoint: http://localhost:4040/mcp
	@exec echo
	@exec echo Define this endpoint in your MCP client configuration
	@exec echo
	earthdata-mcp-server start \
	  --transport streamable-http \
	  --port 4040

release: ## tag the version in __version__.py; the Release workflow publishes it
	@test -z "$$(git status --porcelain)" || (echo "The working tree is not clean" && exit 1)
	git tag -a v$(VERSION) -m "Release $(VERSION)"
	@echo
	@echo "Push the tag to publish: git push origin v$(VERSION)"
