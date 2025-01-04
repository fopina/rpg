---
title: "0x308D Mutual TLS, Singular CommonName"
date: 2024-12-02T23:32:10Z
draft: false
toc: false
images:
tags: 
  - traefik
  - mtls
---

Traefik supports [client authentication (mTLS)](https://doc.traefik.io/traefik/https/tls/#client-authentication-mtls), allowing client certificates issued by a given CA to be required to connect to some services.

However, it does not support filtering only by a subset of Subject CNs (common names).

One could use multiple CAs, one per device/user or one per service, to have this granularity but it's not very practical for either management or configuration.

## TL; DR;

Use [traefik-commonname-validator-plugin](https://github.com/fopina/traefik-commonname-validator-plugin) middleware to solve this.

## Deets

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
      +String beakColor
      +swim()
      +quack()
    }
    class Fish{
      -int sizeInFeet
      -canEat()
    }
    class Zebra{
      +bool is_wild
      +run()
    }

```