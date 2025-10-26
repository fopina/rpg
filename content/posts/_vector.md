---
title: "??? Vector? Very fluent, not a bit"
date: ...
draft: false
toc: false
images:
tags: 
  - logs
  - metrics
---

I was a fan of fluentbit (wrote about it), small footprint (even more coming from the same guys of memory hogging fluentd) and very performant. But I've opened a few pull requests to their repo (link with author filter), and all blantly ignored/dismissed without real reason for it.

The plugin system works well so I ended up forking some of those changes into standalone plugins but eventually I had to update them. It'd be much nicer to have them upstream.

Then I found out about vector (link). (blablabla why move to it?)

Migration

Current fluentbit integrations:

* add hostname to every record
* inputs: cpu (just cpu_p for dashboards), mem2, netif, diskfree,
* output: influx
* input: systemd (for dockerd logs), docker stats
* output: loki
* input: thermal and scaling for Pis
* input: kmsg

---

setup basic vector with host metrics to compare how it looks in influxdb (get it to look exactly the same)
