---
title: "0xF404 Mono Price, Mini Print"
date: 2020-12-09T23:38:59Z
draft: false
toc: false
images:
tags: 
  - 3dprinting
  - review
  - monoprice
---

## TL;DR;

One year ago I bought a [MP Mini Delta](https://www.monoprice.uk/collections/3d-printers/products/monoprice-mp-mini-delta-3d-printer), my final review:

Pros:
* *Cheapest I could find* - bought it £91
* *Really compact* - perk of the [delta](https://3dinsider.com/what-is-a-delta-3d-printer/) style and the very small print bed, fits perfectly in a normal desk corner, no need for huge workbenches like most of the others
* *Sturdy, portable* - sturdy build and an handle makes it easy and trouble-free to move around
* *Heated bed* - rare in cheap printers

Cons:
* *WiFi* - should be a *PRO* as it is uncommon in cheap printers, but it simply doesn't work
* *Print bed* - 11cm *diameter* is quite small
* *Support* - it's just ridiculous how bad it is


## The Search

One year I decided it was time to get a 3d printer.  
In a previous company I had to [prototype](https://www.openscad.org/) a few boxes and printed them on a [Bee](https://shop.beeverycreative.com/produto/beethefirstplus/).  
When I moved into a new job, there was a [Anet A8](https://www.anet3d.com/product/a8-plus-diy/) to play but a lot of people used it and left it broken.

As 3d printers were becoming cheaper and cheaper I decided it was time to look for one, thought it had to:
* cheap - not serious into 3d printing
* compact - not too much space in my apartment home office

I wouldn't mind if it was complex to setup and maintain as long as it paid off for flexibility (eg: extruders for different materials) or other benefits, but it definitely had to be smaller than *Anet A8*

Then I found [MP Mini Delta](https://www.monoprice.uk/collections/3d-printers/products/monoprice-mp-mini-delta-3d-printer).
* Cheap  :white_check_mark: - seriously couldn't find anything cheaper...
* Compact :white_check_mark: - small yet everything well protected inside a sturdy steel build
* Ready to use - unexpected but nice!

I also read `11cm` for the print bed but missed the *circular*, so I thought it was a perfect size for raspberry pi cases and all... (but wrong :x:)

Promptly ordered it :package: 

## First Blood

As soon as I unboxed the printer, I admit, I was positevely surprised by the looks of it.

Pulled out the manual, inserted the SD card that comes with it and in less than 10 minutes after unboxing (*literally*) it was printing out the test [maneki-neko](https://en.wikipedia.org/wiki/Maneki-neko).  
Definitely amazed how simple and fast it was.

A little over 2h after, the print was done and quality was quite decent (much better than expected).

First setback though, finally noticed that print bed had `11cm` of *diameter*, not square size. That means only a square of `7.7cm` is possible, quite the difference... Oh well.

## Pull Back

Now that the print test was done, I needed to print something of mine to see how it worked out.

The SD card had the `.gcode` for the maneki-neko, an installer of `Cura 15.04.6`, Cura profile settings for the printer and digital version of the manual. Whole content backed up (and shared) [here](https://github.com/fopina/mp-mini-delta-cura/tree/main/original-but-old).

But no Mac version. Googling a bit `Cura 15` was a legacy version, it was now [Ultimaker Cura](https://ultimaker.com/software/ultimaker-cura) and new version scheme.  
So I download that one. Surprise, USB printing had been removed.

But WiFi printing is supported. I saw WiFi mentioned in the manual, let's set it up!  
The manual says to download `MP 3D Printer WiFi Connect` app from Play Store or iTunes, but no direct links.  
I look them up, nothing. There was only an app called `MP Mini 3D Printer Client & Connect.` (but no longer available either today) but it was from random individual (later found out he was part of the [MP community](https://www.mpminidelta.com/)) not from Monoprice. And only for Android.

So I drop them an email:

> From: me  
> Received: Thu Nov 14 2019 16:35:16 GMT-0800 (Pacific Standard Time)  
> To: tech@monoprice.com; Technical Support;  
> Subject: wifi connect mobile app  
> 
> Hello, where can I find the mobile apps for wifi connection? Android or iOS, I cannot find either...

I get this reply:

> From: Tech <Tech@monoprice.com>  
> Nov 15, 2019, 5:26 PM  
> 
> Good Morning!  
> What I would suggest is go to Google Play Store on an Android device. Search "MP 3D Printer Wifi Connect" one of the first options after searching should be "MP Mini 3D Printer Client & Connect." Download that program and follow the instructions. There is also instructions inside the manual for the MP Mini Delta 3D  Printer. If you don't have the manual on hand you can go to the Monoprice website search the printer, at the bottom of the printer product page is a link to the Manual. If you have any other questions or need any help I am more than happy to help out. Have a great day!

I reply that I had done it but it wasn't the official app, so they say:

> From: Tech <Tech@monoprice.com>  
> Nov 15, 2019, 7:14 PM  
>
> Thank you for the additional information. I am new and it was brought to my attention that that particular program is not an official app, I'm sorry for suggesting that one. Unfortunately the best we could do is suggest you go to the Wiki community page that it sounds like you already went to and follow their tutorials, besides that we can't assist with the Wifi connection because we don't currently have any official applications or guides to assist with. Just in case we are talking about two different websites I will provide the link to the Wiki page we always suggest. Outside of that I do want to make sure that it is known that our 3D Printers all only work off a 2.4ghz Wifi signal, so the first thing I would do is make sure you are trying to connect to a 2.4ghz Wifi signal. If I can assist in any other way, please E-mail me back. Have a great day!
> MP Mini Delta 3D Printer wiki page: https://www.mpminidelta.com/

So the official support reply for a standard feature not working is to get support from community... :facepalm:

I follow community instructions for [connecting to WiFi](https://www.mpminidelta.com/wifi/g-code_file) (.gcode mirrored [here](https://github.com/fopina/mp-mini-delta-cura/blob/main/original-but-old/wifi_setup.gcode)) and I can open the printer webpage from my laptop.

Great, so I thought. Trying to add `network printer` in Cura simply fails all the time, so I take the [test cat .gcode](https://github.com/fopina/mp-mini-delta-cura/blob/main/original-but-old/auto00-demoCAT.g) and upload it directly from the browser. I'd still be pratical if I could just load the prints that way (after slicing in Cura).  
But no, at 9% upload, every time, printer stops responding and only turning it off and back on makes it reponsive again... Tried another (smaller) .gcode and same...

I ping the support again

 > Understood, just to confirm you are running the printer on a 2.4ghz Wifi correct? The SD card should only have the gcode file on it, if it has anything else you might want to clear it out. As per it failing, even when the Wifi setup is working correct there is always a chance that a file will fail when trying to upload a file through Wifi. From our experience we've notice that SD card printing is much more reliable than Wifi printing as there are no issues with file transfer. SD card has the best resolution over Wifi and USB. Wifi at best is finicky on transferring files over to the SD card and can experience lag drops. If you have any other questions please E-mail me back. 

 Again, printer supports WiFi officially but `it's flaky and you should use SD card (not even USB)`...

## Octoprint

Gave up on WiFi.

Every 3D print search eventually goes through some [octoprint](https://octoprint.org/) link. As I already had a few Pis up and running (as a docker swarm cluster), I decide to plug the printer into one and try it (and built [this docker image](https://github.com/fopina/docker-octoprint) to use it)

The USB device is detected but every time I click connect it fails. Google leads me to [this plugin](https://mpminidelta.com/octoprint/serial_double_open_plugin), specifically to solve this issue in these models...  
And finally, I can print the damn cat without the SD card.

## Slicing

Back to Cura to generate some .gcode by myself (can't print the cat in a loop), the printer is not part of the default profiles. And the profile in the SD card (for `Cura 15.04.6`) is not compatible.

Reaching out to community again, a facebook group maintains [a profile](https://www.mpminidelta.com/slicers/cura).  
I set it up, draw a cube in OpenSCAD, slice up the .STL with this profile, load the .gcode in OctoPrint and happily see it print with success.

Currently, this profile (from the MPMD Facebook group) has been added to [Cura source tree](https://github.com/Ultimaker/Cura/blob/master/resources/definitions/mp_mini_delta.def.json), so installing profile separately is no longer required!

## Redemption

At some point, I had some warped prints and reached out to support again. They suggeted using [this](https://github.com/fopina/mp-mini-delta-cura/blob/main/start_code.gcode) as `Start Gcode` in the profile. It did seem to solve the issue.  
Not using it anymore, but saving it here in case it happens again.

## Conclusion

For the price, I couldn't ask much from the support, but maybe they could state that somewhere, that they don't support their own printer. And I'd buy it anyway, after finding out about the small yet strong community.

Apart from the support, print-wise, I'm quite happy with it and I strongly recommend it as a `cheap, compact, ready-to-use` printer, if you have a raspberry pi (or anything else) to use with OctoPrint.
