.PHONY: separate combined original

.venv:
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt

separate: .venv
	cd separate && make

combined:  .venv
	cd combined && make

original:  .venv
	cd original && make
