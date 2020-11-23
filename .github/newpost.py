#!/usr/bin/env python3

import random
import os
from pathlib import Path


def main():
	done = {
		x.stem[:6]
		for x in (Path(__file__).parent.parent / 'content' / 'posts').glob('0x*')
	}
	random.seed(0)
	post_id = '0x0000'
	while post_id in done:
		post_id = '0x%04X' % random.randint(0x0, 0xffff)
	os.execvp('hugo', ['hugo', 'new', 'posts/%s.md' % post_id])


if __name__ == '__main__':
	main()
