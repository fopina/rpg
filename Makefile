all:
	hugo -DFw serve

new:
	.github/newpost.py
