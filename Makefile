PYTHON   ?= python3
ENV_DIR  ?= .venv
SRCS = $(shell find src/ -type f -name '*.py')
ART = $(shell find src/art -type f -name '*')
all:
	echo "meh"

.venv/bin/activate:
	python3 -m venv .venv

.venv/touchfile: .venv/bin/activate requirements.txt
	. .venv/bin/activate && pip install -r requirements.txt
	>$@

venv: .venv/touchfile
	@echo "venv meh"

dist/wxPick.app: .venv/touchfile wxPick.py $(SRCS) $(ART)
	. .venv/bin/activate && python setup.py py2app

clean:
	find . -iname "__pycache__" -delete
	rm  -rf .venv/ build/ dist/

.PHONY: clean run

build: dist/wxPick.app
	@echo "build meh"

app: build
	./dist/wxPick.app/Contents/MacOS/wxPick

run: venv
	. .venv/bin/activate && python -m wxPick