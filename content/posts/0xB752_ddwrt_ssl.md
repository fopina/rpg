---
title: "0xB752 ddwrt + custom certificate"
date: 2021-02-14T16:26:09Z
draft: true
toc: false
images:
tags: 
  - ddwrt
  - router
  - ssl
  - certificates
---

When I first installed [dd-wrt](https://dd-wrt.com/) (no support from [openwrt](https://openwrt.org/)) on [my router](https://www.netgear.com/home/online-gaming/routers/xr500/), I enabled HTTPS-only access for the web UI.  
When the nasty prompt from the self-signed certificate popped up, I looked for an option to upload my own cerficate (signed by the internal CA I use).  
There was none...

Left it be for quite soem time, but finally decided to sort it out and, to my surprise, there's no official documentation on it (or not easy to find, at least)...

Found [this thread](https://forum.dd-wrt.com/phpBB2/viewtopic.php?t=27979) on their forum which basically set two options:
* using [firmware mod kit](https://forum.dd-wrt.com/wiki/index.php/Development#Firmware_Modification_Kit) to embed your cert into the image before flashing (no need to recompile at least...)
* enable JFFS, save the cert (and key) there and use a startup script to `mount -o bind` those on the default `/etc/cert.pem` and `/etc/key.pem` locations

I found it hard to believe that dd-wrt had no GUI setting for a custom SSL cert, even more that there wouldn't be some `nvram` setting to store one, at least using ssh...

Both options would be ok, but I decided to take a quick look at dd-wrt code and found [this](https://github.com/mirror/dd-wrt/blob/088ba261dfe84e43e5954dd66e9ced02c01a1a95/src/router/httpd/httpd.c#L1564-L1583):

```c
#if defined(HAVE_OPENSSL) || defined(HAVE_MATRIXSSL) || defined(HAVE_POLARSSL)
		char *cert = nvram_safe_get("https_cert");
		char *key = nvram_safe_get("https_key");
		char *certfile = NULL;
		char *keyfile = NULL;
		if (*cert) {
			certfile = "/tmp/https_cert";
			writenvram("https_cert", certfile);
		}
		if (*key) {
			keyfile = "/tmp/https_key";
			writenvram("https_key", keyfile);
		}
		if (!certfile)
			certfile = nvram_safe_get("https_cert_file");
		if (!*certfile)
			certfile = CERT_FILE;
		if (!keyfile)
			keyfile = nvram_safe_get("https_key_file");
		if (!*keyfile)
			keyfile = KEY_FILE;
#endif
```

Taking a look at blame it points to [rev 44703](https://github.com/mirror/dd-wrt/commit/e27ffb50f592a58a392c789a24e2e681eb298112), so sort of recent.  

It seems before it already supported specifying a custom location but only if was compiled with `HAVE_CUSTOMSSLCERT` :shrug:

```c
#ifdef HAVE_CUSTOMSSLCERT
		if (SSL_CTX_use_certificate_file(ctx, certfile, SSL_FILETYPE_PEM)
		if (SSL_CTX_use_certificate_file(ctx, nvram_safe_get("https_cert_file"), SSL_FILETYPE_PEM)
#else
		if (SSL_CTX_use_certificate_file(ctx, CERT_FILE, SSL_FILETYPE_PEM)
#endif
```

Anyway, I haven't found these new nvram settings documented anywhere, so I'll highlight them here:

* `https_cert` / `https_key` - set them to the raw content of a cert / key and done, no need to store them anywhere in the router filesystem (so it does not require JFFS enabled)
* `https_cert_file` / `https_key_file` - set them to the paths to each respective file, so you'll have to enable JFFS (or embed in the image, though that wouldn't make much sense - just overwrite the default one). I assume this might be helpful if [Let's Encrypt](https://letsencrypt.org/) (or any other form of short-lived certs) are used and it's easier to replace a file that push to `nvram`. Or maybe if a very long chain of trust is used in the cert...?

I went with the cleanest option of putting cert and key directly in `nvram`:

* generate certificate with [minica](https://github.com/jsha/minica)
```
minica -ca-cert .. -ca-key .. -domains myrouter.internal -ip-addresses 192.168.1.1
```
* ssh to router and set the `nvram` keys:
```
$ nvram set https_cert='-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----'
$ nvram set https_key='-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```
* reload web UI
```
$ stopservice httpd
$ startservice httpd
```
