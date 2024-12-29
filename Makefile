IMAGE := ghcr.io/hugomods/hugo:reg-0.111.3

all:
	docker run --rm -p 1313:1313 -v $(PWD):/src $(IMAGE) hugo -DFw serve --bind 0.0.0.0

new:
	.github/newpost.py

build:
ifeq ($(CF_PAGES),1)
ifeq ($(CF_PAGES_BRANCH),main)
	hugo --minify
else
	hugo --minify -b $$CF_PAGES_URL
endif
else
	docker run --rm -v $(PWD):/src $(IMAGE) hugo --minify
endif