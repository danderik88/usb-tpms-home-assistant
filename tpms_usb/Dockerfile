FROM ghcr.io/home-assistant/aarch64-base:latest
RUN apk add --no-cache python3 mosquitto-clients
COPY run.sh tpms.py /
RUN chmod +x /run.sh
CMD ["/run.sh"]
