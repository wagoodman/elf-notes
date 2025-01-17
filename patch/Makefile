.PHONY: build scan run

all: build scan run

build:
	docker build -t patch:demo .

scan:
	@mkdir -p sboms
	syft patch:demo -o table -o json=sboms/syft.json
	jq '.artifacts[]' sboms/syft.json

run:
	docker run --rm -it patch:demo
