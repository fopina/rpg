---
title: "??? Magic Switch"
date: ...
draft: false
toc: false
images:
tags: 
  - apple
  - mouse
  - keyboard
  - kvm 
---

Apple is CRAZY expensive, unless you really value the small differences its products have... Then it's _just_ very expensive!

I do value some of those differences, yet one huge annoyance is switching across devices with magic mouse/keyboard. Yes, "Universal Control" is not the answer to everything, I don't want to have both laptops connected when I'm using just one of them.

I switch one single cable between both laptops and everything works via the docking station (power delivery, monitors, usb devices...) _except_ keyboard and mouse as they're bluetooth. Shouldn't bluetooth devices be the easy ones?

I'm sure with older versions of MacOS (when we could disable bluetooth wake up! - link?), when one mac went to sleep, the other mac could connect to mouse/keyboard. But not it cannot.

And every single post I can find online wraps up with "just connect the lightning cable to pair" which is far from satisfactory. If I wanted to connect tables, I'd have USB mouse and keyboard and no issues...

That being said, I did find a comment somewhere (can't remember where) mentioned to "forget devices" in one device and then re-pair in the other one. While this would be even worse than plugging cable, it can be automated, so I did: https://gist.github.com/fopina/71345e937195d88f98899420f147d8b5

> **dependencies** `brew install blueutil`

-- now left to trigger it whenever docking station is plugged or unplugged --

Decided to give copilot and chatgpt a go on how to trigger a script when USB devices or monitors were plugged or unplugged.
It accurately mentioned `system_profile SPblabla` to list current usb devices but for the LaunchAgent it would either suggest `WatchPath` /Volumes or /dev, and neither changed when switching my docking station (that has no USB disks connected to it).
Kept the launchagent definition nevertheless and went off to find some path that would indeed work as I did not want to have the script simply running every X seconds...

# first (failed) try

Found it here - https://stackoverflow.com/questions/20099333/terminal-command-to-show-connected-displays-monitors-resolutions

Final launchd (`launchctl load ~/Library/LaunchAgents/com.skmobi.checksub.plist`):
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-0.1.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.skmobi.checksub</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/fopina/.local/bin/magic_switch_monitor.sh</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Library/Preferences/com.apple.windowserver.displays.plist</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/magic-switch.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/magic-switch-error.log</string>
</dict>
</plist>
```

```
#!/bin/sh

# TODO: redirect all logs to unified logging
# PATH does not have user profile here, add homebrew and .local

export PATH=/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin:${PATH}

cd $(dirname $0)

if system_profiler SPDisplaysDataType | grep -q 'DELL P2722H'; then
  echo "turning on"
  # let the other one turn off first
  sleep 2
  magic-switch on
else
  echo "turning off"
  magic-switch off
fi
```

**above fails because of macos12** 

# final try (works)

blabla usb-trigger written with chatgpt blabla - https://github.com/fopina/usb-trigger/

```
#!/bin/sh

# TODO: redirect all logs to unified logging
# PATH does not have user profile here, add homebrew and .local

export PATH=/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin:${PATH}

if [ "$USB_EVENT" = "attach" ]; then
  echo "turning on"
  # let the other one turn off first
  sleep 2
  magic-switch --notify on --retries 2 --connect
else
  echo "turning off"
  magic-switch --notify off
fi
```

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-0.1.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.skmobi.checksub</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/fopina/.local/bin/usb-trigger</string>
        <string>0x17e9</string>
        <string>0x4307</string>
        <string>/Users/fopina/.local/bin/magic_switch_monitor.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/magic-switch.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/magic-switch-error.log</string>
</dict>
</plist>
```
