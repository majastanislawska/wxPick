PYTHON   ?= python3
ENV_DIR  ?= .venv
SRCS = $(shell find src/ -type f -name '*.py')
ART = $(shell find src/art -type f -name '*')

# ─────────────────────────────────────────────────────────────
# openpnp-capture build & packaging
# ─────────────────────────────────────────────────────────────
EXTERNAL := external/openpnp-capture
BUILD_DIR := $(EXTERNAL)/build

# Final filenames per platform
ifeq ($(OS),Windows_NT)
    CAPTURE_LIB := openpnp-capture.dll
    PLATFORM := windows
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        CAPTURE_LIB := libopenpnp-capture.dylib
        PLATFORM := macos
    else ifeq ($(UNAME_S),Linux)
        CAPTURE_LIB := libopenpnp-capture.so
        PLATFORM := linux
    endif
endif

CAPTURE_TARGET := $(BUILD_DIR)/$(CAPTURE_LIB)
FINAL_LIB := lib/$(CAPTURE_LIB)

# Main target
capture: $(FINAL_LIB)
	@echo "openpnp-capture ready at $(FINAL_LIB)"

# Build openpnp-capture (cross-platform)
$(CAPTURE_TARGET):
	@echo "Building openpnp-capture for $(PLATFORM)..."
	mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR) && cmake .. -DCMAKE_BUILD_TYPE=Release \
		$(CMAKE_FLAGS)
	cmake --build $(BUILD_DIR) --config Release --parallel

# Copy to lib/ (where Python will find it)
$(FINAL_LIB): $(CAPTURE_TARGET)
	@mkdir -p lib
	cp $(CAPTURE_TARGET) $@
	@echo "Copied to $@"

# Clean
capture-clean:
	rm -rf $(BUILD_DIR) lib/$(CAPTURE_LIB)

# # Windows-specific: use MinGW or MSVC
# capture-windows:
# 	$(MAKE) capture OS=Windows_NT CMAKE_FLAGS="-G MinGW Makefiles")

.PHONY: capture capture-clean capture-windows


all:
	echo "meh"

.venv/bin/activate:
	python3 -m venv .venv

.venv/touchfile: .venv/bin/activate requirements.txt
	. .venv/bin/activate && pip install -r requirements.txt
	>$@

venv: .venv/touchfile
	@echo "venv meh"

dist/wxPick.app: .venv/touchfile wxPick.py $(SRCS) $(ART) $(FINAL_LIB)
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