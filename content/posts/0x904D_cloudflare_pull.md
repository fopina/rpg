---
title: "0x904Drop IPTables Drop"
date: 2021-04-09T01:37:29+01:00
draft: false
toc: false
images:
tags: 
  - cloudflare
  - traefik
  - iptables
  - mtls
---

My houselab is made of a few RPis and docker swarm.  
Traefik is used to expose (most of) the swarm services and some of these services are exposed to the internet.

Traefik docker-compose includes these flags
```yaml
 - --entrypoints.http.address=:80
 - --entrypoints.https.address=:443
 - --entrypoints.https_external.address=:8443
```

Home router has port forwarding from 443 to 8443 on one of the manager nodes (where Traefik runs). Binding services to `http` (80) or `https` (443) exposes them internally only, binding to `https_external` (8443) exposes them to the internet.

With this, service exposure is managed in the service docker-compose itself

Internal-only
```yaml
deploy:
    labels:
      traefik.enable: "true"
      traefik.docker.network: traefik_default
      traefik.http.services.myweb.loadbalancer.server.port: 9999
      traefik.http.routers.myweb.rule: Host(`myweb.internal`)
      traefik.http.routers.myweb.entrypoints: http
      traefik.http.routers.myweb.middlewares: https-only
```

Or the extra labels to make it external
```yaml
      traefik.http.routers.myweb_ext.rule: "Host(`myweb.skmobi.com`)"
      traefik.http.routers.myweb_ext.entrypoints: https_external
```

To have some sort of extra security :lock:, all of these domain are behind :cloud: Cloudflare.  
In order to prevent anyone from bypassing it, I was using a simple [ansible role](https://github.com/fopina/ansible-roles/tree/main/cloudflare-ips) in my RPi provisioning playbook to make sure the [latest IP ranges from $NET](https://www.cloudflare.com/ips/) were set up in iptables.

When I read about their [Authenticated Origin Pulls](https://support.cloudflare.com/hc/en-us/articles/204899617) I immediately added it to my backlog, as it's much cleaner to install a CA once than managing IP ranges in iptables.

And it would allow me to also have non-proxied services in the same port (based on SNI), even restrict those to my own client certificates (issued by the [same internal CA I use for server certificates]({{< relref "0x6fd7_docker_internal_ca" >}}))

And it's safer as [IP ACLs are not that reliable](https://jychp.medium.com/how-to-bypass-cloudflare-bot-protection-1f2c6c0c36fb).  

And probably overall performance is even better (*checking rules on every packet versus extra validation on TLS negotiation only*) - **to be tested** :soon:

I left that [Trello card age](https://help.trello.com/article/820-card-aging) for some time like a good wine and finally picked it up!

One quick option would be to spin up an `nginx` container, set it up as cloudflare [documented](https://support.cloudflare.com/hc/en-us/articles/204899617#h_2WFdI4xHJSAQ6GqBjgkfhb), `proxypass` all of it to traefik and change the port forward to nginx port instead.  
But that would require all services behind cloudflare instead of letting me choose per service. Plus, it'd be yet another piece in the stack.

So let's get traefik to handle it!

Traefik has this [tls.options](https://doc.traefik.io/traefik/routing/routers/#options) available both at entrypoint level and router level. But sadly, it's not possible to configure each parameter with labels ([yet](https://github.com/traefik/traefik/issues/5507)).

Enter dynamic configuration! Create some file somewhere, such as `/etc/traefik/dynamic/tlsoptions.yaml`, with

```yaml
tls:
  options:
    cfcert:
      clientAuth:
        caFiles:
          - /etc/traefik/dynamic/origin-pull-ca.pem
        clientAuthType: RequireAndVerifyClientCert
```

Place the [cloudflare-provided origin-pull-ca.pem](https://support.cloudflare.com/hc/en-us/article_attachments/360044928032/origin-pull-ca.pem) and add this conf to traefik (CLI flag)

```yaml
- --providers.file.directory=/etc/traefik/dynamic
```

Now, if some service should be only accessible through cloudflare, I only need to add one extra label, with the new `tls.options` `cfcert`:

```yaml
      traefik.http.routers.myweb_ext.entrypoints: https_external
      traefik.http.routers.myweb_ext.tls.options: "cfcert@file"
```

As most of my exposed services *should* be behind cloudflare, I decided to apply this directly to the entrypoint (traefik CLI flag)
```
      - --entrypoints.https_external.http.tls.options=cfcert@file
```

This makes it the default `tls.option` for any service on entrypoint `https_external` :+1:  
And to disable it, just need to apply label `traefik.http.routers.myweb_ext.tls.options: "default"` to a service.

*NOTE*

*For some reason a label such as `traefik.http.routers.myweb_ext.tls: "true"` resets everything in `tls` back to default. Remove it if you don't need (it should be implicit anyway). If you do need, just re-define `tls.options` as well.*

Unfortunately, setting the `tls.option` at entrypoint level still does not apply to the default router (the 404 shown when no service matches), and I'd really like to have traefik just TLS-reset all those botscan connections...

I tried modifying `default` `tls.options` (instead of naming it `cfcert`) but then it applied to every entrypoint, including the internal ones (which hopefully are never pinged by cloudflare!).

Also found [this](https://www.techjunktrunk.com/docker/2017/11/03/traefik-default-server-catch-all/) to setup a new default service. It seems to work as advertised, matching any request that was not caught by others, but:

```
traefik_traefik.1.lqdaryaciaex@sfpi3    | time="2021-04-09T00:02:07Z" level=warning msg="No domain found in rule HostRegexp(`{catchall:.*}`), the TLS options applied for this router will depend on the hostSNI of each request" entryPointName=https_external routerName=myweb_ext@docker
```

So traefik only binds tls.options based on the configured SNI, not in the SNI requested...

Too bad, but still happy overall with the final setup!

Fun part: I finally did this last week and today cloudflare announced [IP changes](https://www.cloudflare.com/ips/). But no, I don't have to do anything about it (anymore).
