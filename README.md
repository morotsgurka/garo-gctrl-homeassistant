# Garo G-CTRL Home Assistant Integration

![Webel G-CTRL](custom_components/webel_gctrl/brand/logo.png)

## Webel G-CTRL Home Assistant Integration

This repository contains a custom Home Assistant integration for controlling a Webel G-CTRL (GARO) outlet.

Webel Online is a service used by many Swedish parking lots and apartment complexes to control engine heater outlets. This integration lets you control those Webel G-CTRL outlets directly from Home Assistant.

### Features

- Switch entity for turning the outlet on/off.
- Daily energy sensor suitable for the Energy dashboard.
- Calendar view for scheduled events
- Cloud polling (since Webel Online does not provide a public API, the integration scrapes the web interface).

### Installation

1. Copy the `custom_components/webel_gctrl` folder into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **Webel G-CTRL**.

### Configuration

The integration uses the standard Home Assistant config flow:

- Enter your Webel username and password in the UI when adding the integration.
- Credentials are stored securely in Home Assistant and never logged.

You can enable debug logging for troubleshooting by adding the following to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.webel_gctrl: debug
```