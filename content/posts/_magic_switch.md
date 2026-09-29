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


# alternative (and what I actually use now): Hammerspoon

The `usb-trigger` approach above works, but I ended up moving the USB monitoring into [Hammerspoon](https://www.hammerspoon.org/). The Bluetooth work still belongs to `magic-switch`; Hammerspoon replaces `usb-trigger`, its LaunchAgent, and the `magic_switch_monitor.sh` wrapper.

The watcher matches the docking station by its USB vendor/product ID pair (`0x17e9:0x4307` in my case), rather than a UUID. Change that pair for your own dock. In the Hammerspoon console, `hs.inspect(hs.usb.attachedDevices())` lists the attached devices and their IDs.

With Hammerspoon installed and `magic-switch` available at `~/.local/bin/magic-switch` (plus `blueutil` installed as above), save this as `~/.hammerspoon/usb_command_watcher.lua`:

```lua
-- Controls Magic Switch when one configured USB device is connected or disconnected.
--
-- Hammerspoon exposes USB devices as a vendor ID and product ID pair. Configure
-- `deviceID` as "0xvendorID:0xproductID". This watcher replaces the previous
-- usb-trigger match for vendor 0x17e9 and product 0x4307.

local usbCommandWatcher = {}
local activeTasks = {}
local pendingAttach
local homeDirectory = assert(os.getenv("HOME"), "HOME must be set")

local config = {
  deviceID = "0x17e9:0x4307",
  magicSwitchPath = homeDirectory .. "/.local/bin/magic-switch",
  taskEnvironment = {
    HOME = homeDirectory,
    PATH = "/opt/homebrew/bin:/usr/local/bin:" .. homeDirectory .. "/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
  },
  alertMessages = {
    added = "attached",
    removed = "detached",
  },
}

local function deviceID(device)
  return string.format("0x%04x:0x%04x", device.vendorID, device.productID)
end

local function runMagicSwitch(arguments, eventType)
  local task
  task = hs.task.new(config.magicSwitchPath, function(exitCode, stdOut, stdErr)
    activeTasks[task] = nil
    hs.printf(
      "magic-switch command for %s exited with status %d\nstdout:\n%s\nstderr:\n%s",
      eventType,
      exitCode,
      stdOut ~= "" and stdOut or "(none)",
      stdErr ~= "" and stdErr or "(none)"
    )
  end, arguments)

  if not task then
    hs.printf("Could not start magic-switch command for %s", eventType)
    return
  end

  -- GUI apps do not inherit the PATH configured by an interactive shell.
  task:setEnvironment(config.taskEnvironment)
  activeTasks[task] = true
  task:start()
end

function usbCommandWatcher.start()
  usbCommandWatcher.watcher = hs.usb.watcher.new(function(device)
    if deviceID(device) ~= config.deviceID then
      return
    end

    hs.alert.show(config.alertMessages[device.eventType])

    if device.eventType == "added" then
      -- Preserve the old script's delay, allowing the other display to turn off.
      pendingAttach = hs.timer.doAfter(2, function()
        pendingAttach = nil
        runMagicSwitch({ "--notify", "on", "--retries", "2", "--connect" }, "added")
      end)
    elseif device.eventType == "removed" then
      if pendingAttach then
        pendingAttach:stop()
        pendingAttach = nil
      end
      runMagicSwitch({ "--notify", "off" }, "removed")
    end
  end)

  usbCommandWatcher.watcher:start()
end

usbCommandWatcher.start()

return usbCommandWatcher
```

Then add this to `~/.hammerspoon/init.lua` and reload Hammerspoon's configuration:

```lua
require("usb_command_watcher")
```

The module starts its watcher when loaded. Keep Hammerspoon running, and enable launching it at login if you want this available after signing in. It reacts to attach/detach events; loading the configuration does not run `magic-switch` for an already-connected dock.

When the dock attaches, it shows an `attached` alert and waits two seconds before running `magic-switch --notify on --retries 2 --connect`. This gives the other laptop time to release the devices. Detaching shows `detached` and runs `magic-switch --notify off` immediately. If the dock is removed during that two-second window, the pending attach action is cancelled.

The commands run asynchronously through `hs.task`, so the delay and Bluetooth operations do not block Hammerspoon. The module retains references to the running tasks until their completion callbacks run.

One gotcha was `PATH`: Hammerspoon did not inherit my interactive shell's environment, so `magic-switch` initially could not find `blueutil`. The task environment above explicitly includes Homebrew and `~/.local/bin`, with the home directory obtained from `HOME` instead of hardcoding a username.

Every completed command logs its exit status, stdout, and stderr to the Hammerspoon console, including successful runs. I also updated my installed `magic-switch` so `on` returns a nonzero exit code if any device still fails to pair after its retries, and `off` returns nonzero if any device fails to unpair. Those aggregate statuses are returned from `main()` and passed to `sys.exit(main())`, allowing the watcher to report the failure. This does not make every `blueutil` failure fatal: the preliminary unpair and optional `--connect` results during `on` are still ignored.

To retire the previous setup, I unloaded its LaunchAgent and removed its plist:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.skmobi.checksub.plist"
rm "$HOME/Library/LaunchAgents/com.skmobi.checksub.plist"
```

That migration step only applies if the earlier LaunchAgent is installed. With it retired, Hammerspoon handles the USB events and calls `magic-switch` directly; the old monitor shell script is no longer used.
