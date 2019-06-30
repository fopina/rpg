---
title: "0xC53E Peculiar Lenticular"
date: 2019-06-30T18:22:48+01:00
draft: false
toc: false
images:
tags: 
  - diy
  - gifts
---

I needed a symbolic gift [some time ago](https://lmgtfy.com/?q=mother%27s+day+2019) and thought a [lenticular keychain](https://www.alibaba.com/product-detail/2019-Best-Selling-3D-Lenticular-Keychain_62131838666.html?spm=a2700.7724857.normalList.20.5c2525d9YnhbZr&s=p) but shops I found to get a custom made one would take over 2 weeks to deliver.

Googling a bit for DIY seems the only thing required to print lenticulars is image processing and lenticular lens.
Again, getting lenticular lens was not so easy as it looked, so off and found [this video](https://www.youtube.com/watch?v=mmGB9ADKr5Y), that looks easy!

Printing photos, cutting in several stripes and putting them all back together seemed like something to scripted though, hence

{{< gist fopina 6e97829e33de8a8c72c2d1bf65ed5ab9 >}}

### Example

![image 1](/b.png)![image 2](/o.png)

Running

```
python lenticular.py b.png o.png
```

Yields

![result image](/tmp2p9xKb.png)
