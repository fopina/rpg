---
title: "0xF8CB Pi TV - Lock HDMI Configuration"
date: 2020-10-26T12:31:53Z
draft: true
toc: false
images:
tags: 
  - raspberrypi
  - kodi
---

One of my raspberries is connected to the TV (quite original!) running [RetroPie](https://retropie.org.uk/) with Kodi as well.

Every now and then, power fails. When restored, the Pi always came up with messed up resolution.  
I would just reboot it once again and everything would be fine, so I postponed looking into.

Turns out it was one of those things you delay because you think it will take forever to understand but in the end takes 5min...

After a quick check I noticed the Pi would start with the wrong resolution because it booted faster than the TV. That's why reboot the Pi after would pick up the right resolution.

Decided to look into how to set fixed resolution and came across [this forum post](https://www.raspberrypi.org/forums/viewtopic.php?t=71756).

In short:

* Plug TV and boot Pi (so it autodetects the right resolution) and save current settings

  ```
  sudo tvservice -d /boot/edid.dat
  ```

* Then update `/boot/config.txt`

  ```
  hdmi_edid_file=1
  ```
