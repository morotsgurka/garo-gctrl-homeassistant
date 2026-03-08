# Garo G-CTRL Home Assistant Integration

![Webel G-CTRL](custom_components/webel_gctrl/brand/logo.png)

## Webel G-CTRL Home Assistant Integration

This repository contains a custom Home Assistant integration for controlling a Webel G-CTRL (GARO) outlet.

Webel Online is a service used by many Swedish parking lots and apartment complexes to control engine heater outlets. This integration lets you control those Webel G-CTRL outlets directly from Home Assistant.

### Features

- Switch entity for turning the outlet on/off.
- "Until" attribute on the switch showing when an active session will turn off automatically (for example: `22:28`).
- Energy sensor (total-increasing kWh) suitable for the Energy dashboard.
- Calendar view for scheduled events
- Cloud polling (since Webel Online does not provide a public API, the integration scrapes the web interface).

### Installation

#### Install using HACS (recommended)

If you do not have HACS installed yet, visit https://hacs.xyz for installation instructions.

1. In Home Assistant, go to **HACS → Integrations**.
2. Open the menu (⋮) and choose **Custom repositories**.
3. Add this repository's URL as a custom repository and select **Integration** as the category.
4. After adding, use the big **+** button in the bottom-right, search for **Webel G-CTRL**, and install it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration** and search for **Webel G-CTRL** to configure it.

#### Install manually

1. Clone or download this repository.
2. Copy the `custom_components/webel_gctrl` folder into your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and search for **Webel G-CTRL**.

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