---
title: "0x6FD7 docker images and internal CAs"
date: 2021-02-15T01:13:47Z
draft: false
toc: false
images:
tags:
  - docker
  - containers
  - certificates
---

I use an internal CA for all the services in my home lab.  
Big part of the lab is running on docker swarm.  
Usually services connect through internal networks (without using HTTPS as that is offloaded to traefik), but sometimes they do need to validate the certificates (such as interacting with the NAS or router APIs).

For personal images, private CA is naturally bundled into them.  
For public, 3rd party, ones, I usually rebuild them only for that purpose, such as:

```dockerfile
FROM homeassistant/home-assistant:2021.2.3

ADD myCA.pem /usr/local/share/ca-certificates/myCA.crt
RUN /usr/sbin/update-ca-certificates
# for python requests lib...
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

This means that everytime the upstream image is updated, I have to rebuild it (before re-deploy). Pain...

Much simpler option is to bind mount the host trusted certificates in the container (assuming host has the CA setup).

My raspberry Pis (the swarm cluster) have the CA installed with:

```yaml
(tasks - for debian/raspbian)
- name: copy my CA
  copy:
    src: myCA.pem
    dest: /usr/local/share/ca-certificates/myCA.crt
    owner: root
    group: root
    mode: 0644
  become: True
  notify:
    - update trusted ca

(handlers)
- name: update trusted ca
  shell: /usr/sbin/update-ca-certificates
  become: True
```

So any containers running in these hosts can have the system trusted CAs (including internal one) bind mounted with:

```bash
docker run -v /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro \
           -e REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
           homeassistant/home-assistant:2021.2.3
```
