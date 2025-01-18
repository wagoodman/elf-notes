.PHONY: all build run

DOCKER_IMAGE_NAME=image-creator:latest
BINARY_NAME=image-creator
MOUNT_DIR=./mount
BINDIR=bin
SYFT=$(BINDIR)/syft
DEV_BRANCH=add-elf-note-dependencies

all: build run extract-data scan show

build:
	docker build -t $(DOCKER_IMAGE_NAME) .

$(SYFT):
	GOBIN=$(shell pwd)/$(BINDIR) go install github.com/anchore/syft/cmd/syft@$(DEV_BRANCH)

run:
	mkdir -p $(MOUNT_DIR)
	docker run -it --rm -v $(PWD)/$(MOUNT_DIR):/output $(DOCKER_IMAGE_NAME)

extract-data:
	mkdir -p artifacts
	docker create --name temp $(DOCKER_IMAGE_NAME)
	docker cp temp:/symbols.txt artifacts
	docker cp temp:/evidence.txt artifacts
	docker cp temp:/pkg.txt artifacts
	docker cp temp:/libs.json artifacts
	docker cp temp:/notes.json artifacts
	docker rm temp

scan: $(SYFT)
	@mkdir -p sboms
	$(SYFT) $(DOCKER_IMAGE_NAME) -o table -o json=sboms/syft.json

show:
	source ../.venv/bin/activate && python3 ../show.py sboms/syft.json
