.PHONY: build clean

build:
	pyinstaller --onefile --windowed generate_SKU.py

clean:
	rm -rf build/ dist/ generate_SKU.spec
