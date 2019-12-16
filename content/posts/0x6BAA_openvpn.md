---
title: "0x6BAA OpenVPN Made Easy"
date: 2019-12-15T18:54:23Z
draft: false
tags:
 - vpn
 - raspberrypi
 - docker
---

## Why

Some people decide to buy some external VPN service for privacy.  
Personally, as I already commit all my internet usage to my ISP at home, I rather VPN from *untrusted locations* into my home instead, saving a few bucks and keeping my ISP as the sole entity holding that information.  
I guess I could try to use one of those VPN services (with better privacy terms than my ISP) at home but that would increase complexity too much for the rest of the *household*

As I already had some [raspberries](https://www.raspberrypi.org/), [forking](https://github.com/fopina/docker-openvpn/) [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn/) to build it for **arm** was the quickest way, some years ago.

Recently, some people have asked how to use the same docker image quickly in their raspberries, so I took the opportunity to refresh the docker image and add some goodies and I'll summarize the quickstart here.

## How

1. Install [raspbian](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) on your Pi (or any other language that supports docker)
2. Install [Docker CE](https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/debian/)
3. Run this docker

First 2 steps are well documented already, let's focus on the third.

Setting it up in less than 3min

[![asciicast](https://asciinema.org/a/2vyMJDZ76nTQQz3uvIxNyWoCF.svg)](https://asciinema.org/a/2vyMJDZ76nTQQz3uvIxNyWoCF)

### Drill down

1. Initialize the configuration directory
    ```shell
    docker run --rm \
            -v testvpn:/etc/openvpn \
            fopina/openvpn \
            ovpn_genconfig -u udp://my.external.ip:9999
    ```

    `testvpn` used like this will be a [named volume](https://docs.docker.com/storage/volumes/) which is probably the cleanest and easiest option for most cases.  
    If you want to make configuration files available to the host filesystem or if you're using this in a [swarm](https://docs.docker.com/engine/swarm/), then you don't a named volume...  
    `udp://my.external.ip:9999` can be `tcp://` instead if you need to use TCP for some reason, but [avoid if possible](http://sites.inka.de/bigred/devel/tcp-tcp.html).  
    `9999` will be port exposed publicly (in your router, for instance), not the one published by the container - might be the same but not necessarily.

2. Generate CA
    ```shell
    docker run --rm -ti \
               -v testvpn:/etc/openvpn \
               fopina/openvpn \
               ovpn_initpki
    ```
    Nothing much to say, just pick a passphrase for the CA that will be used to issue client certificates.

3. Start the service
    ```shell
    docker run -v testvpn:/etc/openvpn \
               -d -p 9999:1194/udp \
               --restart=always \
               --cap-add=NET_ADMIN \
               fopina/openvpn
    ```
    `-p 9999:1194/udp`
    * you can choose other published port instead of `9999` 
    * Leave the internal port `1194` as that one never changes
    * Adjust `udp` to `tcp` if you used TCP in the first step

4. Generate client configuration
    ```shell
    docker run --rm -ti \
               -v testvpn:/etc/openvpn \
               fopina/openvpn \
               easyrsa build-client-full CLIENTNAME nopass
    ```
    * `CLIENTNAME` should be whatever identifier you want for that profile/device
    * remove `nopass` if you want the profile to have a password (that you will to enter everytime you connect)

5. Generate .ovpn and download link
    ```shell
    docker run --rm \
               -v testvpn:/etc/openvpn \
               fopina/openvpn:helper \
               ovpn_getclient_link CLIENTNAME
    ```
    This will bundle the previous step into an .ovpn file, upload it to [vim.cx](https://vim.cx) (which is a [PrivateBin](https://privatebin.info/) instance that supports attachments) and generate a QR code to make it easier to copy to a mobile device.
    If you prefer to manage the file transfer yourself, you can use:
    ```shell
    docker run --rm \
               -v testvpn:/etc/openvpn \
               fopina/openvpn \
               ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
    ```

## Done: references

* [CLI](https://github.com/fopina/privatebin) used to upload attachments to privatebin
* [CLI](https://github.com/fumiyas/qrc) used to generate the QR codes in the terminal
* [this github workflow](https://github.com/fopina/docker-openvpn/blob/master/.github/workflows/main.yml) to make the multi-platform builds of the docker image

Enjoy your home VPN.
