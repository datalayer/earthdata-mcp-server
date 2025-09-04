# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

SHELL=/bin/bash

.DEFAULT_GOAL := default

.PHONY: clean build

VERSION = "0.0.3"

default: all ## Default target is all.

help: ## display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: clean dev ## Clean Install and Build

install:
	pip install .

dev:
	pip install ".[test,lint,typing]"

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
	docker push datalayer/earthdata-mcp-server:latest

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
	@exec echo curl http://localhost:4040/api/healthz
	@exec echo
	@exec echo 👉 Define in your favorite mcp client the server http://localhost:4040/mcp
	@exec echo
	earthdata-mcp-server start \
	  --transport streamable-http \
	  --document-url http://localhost:8888 \
	  --document-id notebook.ipynb \
	  --document-token MY_TOKEN \
	  --runtime-url http://localhost:8888 \
	  --start-new-runtime true \
	  --runtime-token MY_TOKEN \
	  --port 4040

publish-pypi: # publish the pypi package
	git clean -fdx && \
		python -m build
	@exec echo
	@exec echo twine upload ./dist/*-py3-none-any.whl
	@exec echo
	@exec echo https://pypi.org/project/earthdata-mcp-server/#history
