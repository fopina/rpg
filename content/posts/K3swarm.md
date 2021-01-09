K3swarm

Memory consumption on rest
Master switching (embedded etcd requires 2 nodes / master uses a lot more memory)
Swarm lacks docker features (capabilities)
Kube is so complex...

## To check

* [ ] hostname based routing (traefik)
* [ ] local volumes / NAS
* [ ] privileged containers
* [ ] usb device access
* [ ] compare standy resource usage

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

