# Makefile
COLLECTION_NAME="ciscops.mdd"
COLLECTION_VERSION := $(shell awk '/^version:/{print $$NF}' galaxy.yml)
TARBALL_NAME=ciscops-mdd-${COLLECTION_VERSION}.tar.gz

help: ## Display help
	@awk -F ':|##' \
	'/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)

all: test build publish ## Setup python-viptela env and run tests

$(TARBALL_NAME): galaxy.yml
	@ansible-galaxy collection build

build: $(TARBALL_NAME) ## Build Collection

publish: $(TARBALL_NAME) ## Public Collection
	ansible-galaxy collection publish $(TARBALL_NAME) --token=$(GALAXY_TOKEN)

test: ## Run Sanity Tests
	ansible-test sanity --docker default -v

clean: ## Clean
	$(RM) $(TARBALL_NAME)

.PHONY: all clean test build publish
