add private CA to host

(debian)

```
(tasks)
- name: copy SFHome CA
  copy:
    src: sfhome.pem
    dest: /usr/local/share/ca-certificates/sfhome.crt
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

```
-v /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro
-e REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
