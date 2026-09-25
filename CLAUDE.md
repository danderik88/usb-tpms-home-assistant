# CLAUDE.md

Public repo (github.com/danderik88/usb-tpms-home-assistant): Home Assistant add-on that reads the
433 MHz "USB TPMS for Android" dongle (CH340 1a86:7523, 19200 8N1) and publishes JSON on MQTT
`tpms/state`, plus example HA config in `homeassistant/`.

- **English only, verified facts only.** Nothing goes in the README unless it was checked on the
  real vehicle; unknowns are written as unknown. No personal data (names, IPs, GPS, plates).
- Self-test: `python3 tpms_usb/tpms.py demo` must print `ok`. Stdlib only, no dependencies.
- Bump `version` in `tpms_usb/config.yaml` on every add-on change, or HA will not offer the update.
- The author's camper runs a private copy as local add-on in `../camper-assistant/tpms/` with
  Italian JSON keys (ant_sx, stato...): protocol fixes go in both.
