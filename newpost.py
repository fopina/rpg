#!/usr/bin/env python3

import random
import os


def main():
	count = len([
		x 
		for x in os.listdir(
			os.path.join(
				os.path.dirname(__file__),
				'content', 'posts'
			)
		)
		if x[:2] == '0x'
	])
	post_id = 0
	random.seed(0)
	for _ in range(count):
		post_id = random.randint(0x0, 0xffff)
	os.execvp('hugo', ['hugo', 'new', 'posts/0x%04X.md' % post_id])


if __name__ == '__main__':
	main()
