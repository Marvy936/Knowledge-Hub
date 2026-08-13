# RabbitMQ Routing Key

A direct-exchange troubleshooting challenge. The queue is bound with the wrong routing key, so a published event is not routed to the intended consumer queue.

```bash
docker run --pull=always --rm -it --privileged ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest rabbitmq-routing-key
```
