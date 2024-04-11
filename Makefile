all:
	hugo -DFw serve

new:
	.github/newpost.py

build:
ifeq ($(CF_PAGES),1)
ifeq ($(CF_PAGES_BRANCH),production)
	hugo --minify
else
	hugo --minify -b $$CF_PAGES_URL
endif
else
	hugo --minify
endif