---
title: "0xCF53 Remote, Garage Remote"
date: 2020-11-01T18:40:57Z
draft: true
toc: false
images:
tags: 
  - raspberrypi
  - eletronics
  - domotics
---

## Dr. No Open

One of my garage remotes stopped working but I kept it in hope one day I'd make a learning exercise out of repairing it.

The other day somehow I brought it up in a conversation and it was highlighted that it is common for the push button to wear out, so I opened the remote and tested by shorting over the button with a wire.  
And the garage door opened (thanks Dad)!

{{< imgproc src="remote_1.jpeg" op=Resize args="150x" tags=inline >}}
{{< imgproc src="remote_2.jpeg" op=Resize args="150x" tags=inline >}}
{{< imgproc src="remote_3.jpeg" op=Resize args="150x" tags=inline >}}

Instead of replacing the push button why not use a raspberry to enable the remote?  
Then a webapp could open the garage door?  
> Alexa, ask Home Assistant to open garage

## From StackOverflow With Love

I have used [relay switches](https://en.wikipedia.org/wiki/Relay) in the past to open [maglocks](https://en.wikipedia.org/wiki/Electromagnetic_lock) but the loud *clack* was annoying and mechanical sounded unnecessary.

Picked up a multimeter and measured at the push button:
* V=10v (opener uses 12v battery)
* I=4mA

Looking into alternatives considered using a simple transistor but sharing GND between the garage opener (12v) and the raspberry (3v3) didn't sound safe.

Dove into the huge world of ICs (thanks x7!) and, overwhelmed with the options, Google led me exactly to [this post in SO](https://electronics.stackexchange.com/questions/76682/shorting-a-remote-control-pushbutton-with-gpio-and-a-transistor). Should've started with that...

An octocoupler, LED on one side, transistor with photosensor on the other side. Two isolated circuits, nice one!

According to [this](http://www.mosaic-industries.com/embedded-systems/microcontroller-projects/raspberry-pi/gpio-pin-electrical-specifications#rpi-gpio-input-voltage-and-output-current-limitations), no more than 16mA should be drawn from an output pin in the GPIO and I had a bunch of 330 ohm resistors:

* `3v3 = 330 ohm * I` > `I = 10 mA`

Open up [4N25 datasheet](https://www.digikey.com/en/products/detail/lite-on-inc/4N25/385762): LED on pins 1 and 2 and emitter and collector on 4 and 5.

Schemed it in [Digikey](https://www.digikey.pt/schemeit/project/rgr1-cc1bac87b73e494884bbe0246aa2afe0/), then plugging the bits into a breadboard and connecting to a [Pi 0 WiFi](https://www.raspberrypi.org/products/raspberry-pi-zero-w/?resellerType=home):

{{< imgproc src="scheme1.png" args="500x" >}}
{{< imgproc src="basic.jpeg" args="300x" >}}

```bash
# shell over python, just for fun
# export pin to userspace
echo "18" > /sys/class/gpio/export
# Sets pin 18 as an output
echo "out" > /sys/class/gpio/gpio18/direction
# "push" the button
echo "1" > /sys/class/gpio/gpio18/value
# for 3 seconds
sleep 3
# release
echo "0" > /sys/class/gpio/gpio18/value 
```

And Sesame is open.

## You Must Live Twice

All good and simple, but what about feedback? If the garage opener battery is dead, the Pi cannot *see* it anywhere...

Let's use a second GPIO pin as input and enable it with the current from the opener!  
But the Pi works on 3v and the opener is working on 10v...  
Déjà vu, another 4N25 it is then, the other way around: input will be the garage opener and the output will be connecting Pi 3v3 to the input GPIO pin.

* Updated the scheme in [Digikey](https://www.digikey.pt/schemeit/project/rgr1-cc1bac87b73e494884bbe0246aa2afe0/b59742577e02417988ec0c8ade0acb29)

{{< imgproc src="scheme2.png" args="500x" >}}

* Applied it in the breadboard

{{< imgproc src="basic_2.jpeg" args="300x" >}}

And there: enabling GPIO 18 will enable the opener that then enables GPIO 24. If opener battery is dead, it won't trigger the second 4N25, not enabling GPIO 24.

In this setup, there's no GND connected to GPIO 24 so the GPIO setup needs proper `pull_up_down`:

```python
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
```

## Pentapussy

Time to trim a stripboard and solder!

{{< imgproc src="penta1.jpeg" args="x250" tags=inline >}}
{{< imgproc src="penta2.jpeg" args="x250" tags=inline >}}



## Licence to Click

https://github.com/warthog618/gpio