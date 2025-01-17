.PHONY: build scan show

all: build scan show

build:
	docker build -t patch:demo .

scan:
	@mkdir -p sboms
	syft patch:demo -o table -o json=sboms/syft.json

show:
	source ../.venv/bin/activate && python3 ../show.py sboms/syft.json
