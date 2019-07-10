---
title: "0xD755 Free Log Collection"
date: 2019-07-10T00:47:31+01:00
draft: false
toc: false
images:
tags: 
  - gcp
  - logs
  - cloud
  - fluentd
  - fluentbit
---

I have a few [raspberries](https://www.raspberrypi.org/) lying around the house plus a couple of ~~really cheap~~ low-end VPS (1€ [arubas](https://www.arubacloud.com/))

Not only they there are containers, cron jobs, etc spread among them (but all keep under ansible control) 2 of them are a docker swarm cluster with replicas for same services.

Eventually I need to check logs for something (and I'd also like to keep tabs on cpu/memory/disk metrics), so I started looking into log management/collection solutions.
As these are for personal projects, I always try to go for ~~free~~ low-cost solutions.

Self-hosting [Graylog](https://www.graylog.org/) or [Splunk Free](https://www.splunk.com/en_us/software/features-comparison-chart.html) is not an option as they would barely run on any of these options, plus avoiding storage costs is nice.

* [Loggly](https://www.loggly.com/plans-and-pricing/) has a nice free Lite plan
* [Papertrail](https://papertrailapp.com/plans) has a really shitty one

Probably a few more out there that I could not find before bumping into.... [GCP Stackdriver](https://cloud.google.com/stackdriver/)
Thanks to the always-free plan Google and Amazon now have, Stackdriver is also included there. With 50GB ingestion per month!

Quickly testing [their setup guide](https://cloud.google.com/logging/docs/agent/installation) in one of my VPS gets the logs flowing into (and showing in) [Log Viewer](https://console.cloud.google.com/logs/viewer), awesome!

Issue **uno**: they only have a _x86_ package (as they only support GCP and AWS VMs) and that would leave raspberries out of the party... But looking at the package content it is just embedded ruby with [fluentd](https://www.fluentd.org/) and [their own output plugin](https://github.com/GoogleCloudPlatform/fluent-plugin-google-cloud) gems installed.
Installing the gems (in a ruby docker) in one of the raspberries and it was working.

But this brings up Issue *dos*: ruby!
Who uses ruby? Why?
Fluentd immediately started with 100MB of used memory and grew up to 300MB. Tuning garbage collector helped a little, but not nearly enough. Can't have the log collector using 10 or 15% of the server memory...

Ranting about it at work, someone mentions [Fluentbit](https://fluentbit.io/), fluentd in C (with Go plugins)!
Good looking [documentation](https://docs.fluentbit.io/manual/installation/td-agent-bit) and in an hour or so, I had the logs in Stackdriver but using 1% of memory instead of 10%!

Instead of writing how to set it up or install it, I'll leave ansible to show for itself, with the role and playbook I used to then apply this to every machine.

The _generic_ role:

{{< gist fopina c0439fa29bb7f3fa541a2d81a3f4a1e7 >}}

And the playbook to set it up in all the machines

{{< gist fopina eea83d290f634566b2e68e31d9ba6a74 >}}

Docker was configured (in another role) with `journald` as default logger, that's why I'm using [systemd input](https://docs.fluentbit.io/manual/input/systemd).
Also added a few modify filters to reduce the clutter (and avoid hitting the ingestion limit at some point).

Pushing cpu and memory to use [Logs-based metrics](https://console.cloud.google.com/logs/metrics), but that'll be for another day...
