---
exclude_from_blog: true
title: Writing a Nanopublication
---

```shell
ssh-keygen -t rsa -b 4096 -f ~/.nanopub/id_rsa -C "anatoly@iolanta.tech"
pyld get yaml-ld.yamlld | rdfpipe -i json-ld -o trig - > yaml-ld.trig
nanopub sign yaml-ld.trig
```
