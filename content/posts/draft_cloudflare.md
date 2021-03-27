in my houselab, some of the services are exposed to the internet.

(traeffik setup -> external port 8443 -> 443 on router)

To have some sort of extra security, it sits behind Cloudflare WAF so the docker swarm provisioning ansible playbook takes care of retrieves cloudflare IP ranges and setting up iptables.

I've wanted for some time to switch from iptables to mTLS (with Cloudflare Origin CA), as it's much cleaner to install a CA than managing IP ranges in iptables. And safer as [IP ACLs are not that reliable](https://jychp.medium.com/how-to-bypass-cloudflare-bot-protection-1f2c6c0c36fb).

Also, properly preparing traffik for validating client certs would allow, not only validating Cloudflare requests, but also expose private services with restricted access using my internal CA.

