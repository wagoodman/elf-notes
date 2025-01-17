.PHONY: build scan compare show

all: build scan compare

.venv:
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt

build:
	docker build -t fedora:demo .

scan:
	@mkdir -p sboms
	syft fedora:42@sha256:19fcecbd14f2c1e887cbeb974295f5fc0e7b81e2df133e4f1b47a6f65cd11737 -o json=sboms/latest.json
	syft fedora:demo -o json=sboms/demo.json

show:
	@mkdir -p txt
	@echo "\nLatest Fedora Image"
	@jq -r '.artifacts[] | "\(.name): \(.version) \(.type)"' sboms/latest.json | sort | tee txt/latest.txt

	@echo "\nDemo Fedora Image"
	@jq -r '.artifacts[] | "\(.name): \(.version) \(.type)"' sboms/demo.json | sort | tee txt/demo.txt

compare: show .venv
	@echo "\nComparing Latest and Demo Fedora Images"
	source .venv/bin/activate && python3 diff.py txt/latest.txt txt/demo.txt
