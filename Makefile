# Makefile
COLLECTION_NAME="cisco.cml"
COLLECTION_VERSION := $(shell awk '/^version:/{print $$NF}' galaxy.yml)
TARBALL_NAME=cisco-cml-${COLLECTION_VERSION}.tar.gz
PYDIRS="plugins"

help: ## Display help
	@awk -F ':|##' \
	'/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)

all: test build publish ## Setup python-viptela env and run tests

$(TARBALL_NAME): galaxy.yml
	@ansible-galaxy collection build

build: $(TARBALL_NAME) ## Build Collection

publish: $(TARBALL_NAME) ## Publish Collection
	ansible-galaxy collection publish $(TARBALL_NAME)

format: ## Format Python code
	yapf --style=yapf.ini -i -r *.py $(PYDIRS)

test: $(TARBALL_NAME) ## Run Sanity Tests
	$(RM) -r ./ansible_collections
	ansible-galaxy collection install --force $(TARBALL_NAME) -p ./ansible_collections
	cd ./ansible_collections/cisco/cml && git init .
	cd ./ansible_collections/cisco/cml && ansible-test sanity --docker default -v --color
	$(RM) -r ./ansible_collections

clean: ## Clean
	$(RM) $(TARBALL_NAME)
	$(RM) -r ./ansible_collections

.PHONY: all clean build test publish
