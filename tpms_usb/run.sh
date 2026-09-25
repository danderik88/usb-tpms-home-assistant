#!/usr/bin/with-contenv bashio
H=$(bashio::services mqtt host); P=$(bashio::services mqtt port)
U=$(bashio::services mqtt username); W=$(bashio::services mqtt password)
# Restart the whole pipe if either side dies (dongle unplugged, broker restart).
while true; do
  python3 -u /tpms.py | mosquitto_pub -h "$H" -p "$P" -u "$U" -P "$W" -r -l -t tpms/state
  bashio::log.warning "pipe stopped, retrying in 10 s"
  sleep 10
done
