---
title: "0x8490 Privileged Swarm Services"
date: 2020-03-07T14:38:07Z
draft: false
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
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
```

But as openvpn is not running in the actual service container, the port is not published in the swarm VIP / routing mesh.
If we can scale it up, it needs to end in different nodes (as there's an host bound port) and to make use of the replicas, we need to use the node IP (not *any* node IP as the usual routing mesh)...

My overkill solution:
* adding some proxy - just used [socat](https://linux.die.net/man/1/socat) in my example
* write an entrypoint script that
  * starts docker container (without binding port) attached to a common network with the service container
  * extract the IP from the new container
  * launch proxy using the same port
  * attach to container (so that main service process is the container itself, not the proxy)
* just use that port in the service description as if it was any other service

To accomplish this, I've created the image [fopina/swarm-service-proxy](https://hub.docker.com/r/fopina/swarm-service-proxy) (built from [this](https://github.com/fopina/docker-swarm-service-proxy))

The stack definition using this is

```yaml
version: '3.1'

services:
  vpnd:
    image: fopina/swarm-service-proxy:1
    command: --rm
             --cap-add NET_ADMIN
             -v /nfs/path/to/openvpn/:/etc/openvpn/
             fopina/openvpn
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      PROXIED_PORT: 443
      PROXIED_PROTO: udp
      PROXIED_NAME: openvpn_real
    ports:
      - 443:443/udp
    deploy:
      mode: replicated
      replicas: 1
```

With this, port is actually published from the service (not to the secondary container) so it makes use of the routing mesh (and it doesn't lock the port in the docker host where it lands).

Syntax remained as close as possible to the initial version: command is used as if it was `docker run <command>`.
* `PROXIED_PORT` is the internal port of the secondary container.
* Use `PROXIED_PROTO: udp` if `socat` should use the UDP labels (instead of TCP).
* Use `PROXIED_NAME` to choose the name *prefix* of the secondary container - yes, *prefix* as random string is appended to it to make sure it will not collide if scaled up.
* Do not forget to bind the port you need in the service
* Do not publish any port on the secondary container (as it won't be used)

So it is now fully managed as it was a service and fully scalable.
