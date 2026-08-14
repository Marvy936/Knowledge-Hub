# Nginx Rate Limiting

A public API is correctly proxied through Nginx, but it has no request throttling. A burst client can send unlimited traffic to the backend.

## Task

Edit `/workspace/nginx.conf` so that:

- requests to `/api/` are limited to **2 requests/second per client IP**;
- a burst of **2 extra requests** is allowed without delay;
- requests above the allowed burst return **HTTP 429**;
- normal requests still proxy to the backend successfully.

Use the normal lab workflow:

```bash
status
check
hint
apply
check
reset
```

The validator sends real HTTP traffic through Nginx. A syntactically correct directive that does not actually throttle requests will not pass.
