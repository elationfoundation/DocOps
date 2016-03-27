.PHONY: all dev_install test docs remove

all: test init

install:
    pip3 install -r requirements.txt

remove:
    pip3 uninstall docops

test:
    py.test tests

dev_install:
    pip3 install --editable -r requirements.txt

docs:
    sphinx-apidoc -F -o docs docops
