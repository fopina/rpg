---
title: "0x8490 Privileged Swarm Services"
date: 2020-03-07T14:38:07Z
draft: true
toc: false
images:
tags: 
  - docker
  - swarm
---

Some docker images require extra capabilities to work, ie:
* openvpn needs `NET_ADMIN`
* anything using USB/i2c will need `--device=/dev/ttyAMA0`

Swarmkit does not support that (nor the GIEF IT ALL `--privileged` flag).

There are a lot of issues on their github(s) such as [this](https://github.com/docker/swarmkit/issues/1030), [this](https://github.com/moby/moby/issues/25885) or [this](https://github.com/moby/moby/pull/38380).

It seems there is consensus into adding the feature to swarmkit though it won't be available before 19.06 or 19.09.

Until then, the best solution seems to be spinning up a service that starts the container after, such as:

```yaml
version: '3.1'

services:
  web:
    image: docker:19.03
    command: sh -c "docker pull fopina/octoprint && docker run 
                        --rm
                        --name octoprint_real
                        -v /nfs/path/to/octoprint/config:/root/.octoprint
                        --device=/dev/ttyAMA0
                        -p 5000:5000
                        fopina/octoprint"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /root/.docker:/root/.docker:ro
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.hostname == printingPi]
```

Why would you use swarm service for this, since it's bound to the specific node where the USB cable is connected?

In this case, it's managing all **services** the same way, I don't want to deploy some with `docker-compose` and others with `docker swarm deploy`...

But in the case of, let's say [openvpn]({{< ref "0x6BAA_openvpn" >}}), it could be useful for easily scaling up across different nodes.

We could use a stack like the first:

```yaml
version: '3.1'

services:
  vpnd:
    image: docker:19.03
    command: docker run --rm
                        --name openvpn_real
                        --cap-add NET_ADMIN
                        -p 443:443/udp
                        -v /nfs/path/to/openvpn/:/etc/openvpn/
                        fopina/openvpn
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    cap_add:
      - NET_ADMIN
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
```

But as openvpn is not running in the actual service container, the port is not published in the swarm VIP / routing mesh.
If we can scale it up, it needs to end in different nodes (as there's an host bound port) and to make use of the replicas, we need to use the node IP (not *any* node IP as the usual routing mesh)...

Possible solution:
* adding some proxy (UDP in this case - or something light for both TCP and UDP like [this](https://github.com/arkadijs/goproxy)) to the service image (together with docker binary)
* write an entrypoint script that
  * starts docker container (without binding port) attached to a common network with the service container
  * extract the IP from the new container
  * launch proxy using the same port
  * attach to container (so that main service process is the container itself, not the proxy)
* just use that port in the service description as if it was any other service

This would very likely solve this but I'd rather wait for 19.06 and use as it is for now ^^
