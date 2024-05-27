K3swarm

Memory consumption on rest
Master switching (embedded etcd requires 2 nodes / master uses a lot more memory)
Swarm lacks docker features (capabilities)
Kube is so complex...

## UPDATE May 2024: WILL / NEED to switch regardless because...

* no privilege
* capabilities took ages to be supported, devices are not yet
* overlay network sucks (?? Issue with keepalived / constant errors in journal)
* no affinity, missed for sidecars
* ... add others ...?

## To check

* [ ] hostname based routing (traefik)
* [ ] local volumes / NAS
* [ ] privileged containers
* [ ] usb device access
* [ ] compare standy resource usage

## setup

* local storage: https://rancher.com/docs/k3s/latest/en/storage/ https://github.com/rancher/local-path-provisioner
* disable traefik: https://rancher.com/docs/k3s/latest/en/networking/#traefik-ingress-controller `--disable traefik`
* exclude lb from some nodes: add `svccontroller.k3s.cattle.io/enablelb` label to the nodes that *should* have lb - https://rancher.com/docs/k3s/latest/en/networking/#traefik-ingress-controller
* deploy traefik2 (after disabling k3s-traefik): https://www.ivankrizsan.se/2020/10/31/hot-ingress-in-the-k3s-cluster/



## resource usage

(test setup https://github.com/fopina/k3s-play)

### k3s

```
 k3s-master
              total        used        free      shared  buff/cache   available
Mem:           985M        676M         87M        1.2M        221M        220M
Swap:            0B          0B          0B
== k3s-worker1
              total        used        free      shared  buff/cache   available
Mem:           985M        184M        319M        732K        481M        663M
Swap:            0B          0B          0B
== k3s-worker2
              total        used        free      shared  buff/cache   available
Mem:           985M        183M        321M        708K        481M        667M
Swap:            0B          0B          0B
```

### swarm

```
== swarm-master
              total        used        free      shared  buff/cache   available
Mem:           985M        159M        195M        592K        631M        684M
Swap:            0B          0B          0B
== swarm-worker1
              total        used        free      shared  buff/cache   available
Mem:           985M        143M        183M        592K        658M        699M
Swap:            0B          0B          0B
== swarm-worker2
              total        used        free      shared  buff/cache   available
Mem:           985M        144M        180M        568K        661M        699M
Swap:            0B          0B          0B
```

### k3s with docker

```
== k3s-master
              total        used        free      shared  buff/cache   available
Mem:           985M        713M         69M        1.2M        202M        197M
Swap:            0B          0B          0B
== k3s-worker1
              total        used        free      shared  buff/cache   available
Mem:           985M        214M        102M        752K        668M        629M
Swap:            0B          0B          0B
== k3s-worker2
              total        used        free      shared  buff/cache   available
Mem:           985M        216M         99M        752K        669M        630M
Swap:            0B          0B          0B
```
