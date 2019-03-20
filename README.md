# My Home Assistant Configuration

This [Home Assistant](https://www.home-assistant.io/) configuration is based on [configuration by Isabella Gross Alström](https://isabellaalstrom.github.io/).

*Описание проекта будет вестись полностью на английском, но я готов помогать и русскоязычным пользователям Home Assistant. Буду рад, если смогу быть полезен в настройке вашего умного дома.*

![](https://img.shields.io/maintenance/yes/2019.svg?style=popout)
![](https://img.shields.io/github/last-commit/Limych/HomeAssistantConfiguration.svg?style=popout)
![](https://img.shields.io/github/issues-raw/Limych/HomeAssistantConfiguration.svg?label=Open%20todos&style=popout)
![](https://img.shields.io/github/issues-closed-raw/Limych/HomeAssistantConfiguration.svg?colorB=green&label=Closed%20todos&style=popout)
![](https://img.shields.io/github/issues/Limych/HomeAssistantConfiguration/bug.svg?colorB=red&label=Bugs&style=popout)

Like the Isabella I'm using the GitHub [issues](https://github.com/Limych/HomeAssistantConfiguration/issues) and [project](https://github.com/Limych/HomeAssistantConfiguration/projects/1) to keep track of bugs in my configuration and new features I want to make/use.

## Organizing the configuration

This configuration is broken down into [packages](https://www.home-assistant.io/docs/configuration/packages/), sort of mini configuration-files. This makes it easy to see everything pertaining to a specific implementation.

But while using packages you can no longer reload your config with the buttons in the ui.

## Ecosystem

Now I have very few devices in the system. But I plan to gradually add new ones.

<details>
    <summary>Click to expand!</summary>

Now I am running Hass.io on my FreeNAS server into Bhyve virtual machine which emulates Raspberry Pi 3 Model B+ 32bit.

* **Personal gadgets:**
    1. Android devices (Phones and Tablets);
* **Media:**
    1. Two [LinkPlay-driven](https://linkplay.com/) Wireless Speakers;
    1. [FreeNAS](https://freenas.org/) File Server;
    1. [Emby](https://emby.media/) Media Server;
* **Network:**
    1. [Transmission](https://transmissionbt.com/) BitTorrent Client;
    1. [Sonarr](https://sonarr.tv/) Monitoring Server;
    1. [Syncthing](https://syncthing.net/) Sync Client;
    1. [Gogs](https://gogs.io/) Git Server;
* **Security:**
    1. [OPNsense-driven](https://opnsense.org/) Network Firewall;
    1. [Beward DS06M](https://www.beward.ru/katalog/ip-videodomofony/vyzyvnye-paneli/vyzyvnaya-panel-ds06m/) Doorbell;
* **Climate:**
    1. Home made [ESP32-driven](https://ru.wikipedia.org/wiki/ESP32) climate sensor (now only indoor Pressure, Humidity & Temperature);

</details>

## Lovelace

I'm using [YAML mode](https://www.home-assistant.io/lovelace/yaml-mode/). Single file splitted to several ones via [includes](https://www.home-assistant.io/docs/configuration/splitting_configuration/).

My main Lovelace-file is found [here](https://github.com/Limych/HomeAssistantConfiguration/blob/master/ui-lovelace.yaml), and my folder with includes [here](https://github.com/Limych/HomeAssistantConfiguration/tree/master/lovelace). This is very much still a work in progress, so files might not correspond exactly to screenshots.

I put a lot of work into making this repo available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=UAGFL5L6M8RN2&item_name=Donation+for+a+big+barrel+of+coffee+:)&currency_code=EUR&source=url"><img alt="Buy Me a Coffe" src="https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/donate-with-paypal.png"></a></p>

### Examples from my Lovelace GUI

I have tried to make a GUI that is [mobile first](https://medium.com/@Vincentxia77/what-is-mobile-first-design-why-its-important-how-to-make-it-7d3cf2e29d00), since that's how I most often look at it.

Click on the images to get to the corresponding YAML-file.

#### Mobile

<details>
    <summary>Click to expand!</summary>

Home view

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/mobile_home.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/00_home_view.yaml)

Home info

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/mobile_home_info.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/10_home_info_view.yaml)

System info

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/mobile_system_info.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/30_system_info_view.yaml)

Automations view

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/mobile_automations.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/00_automations_view.yaml)

</details>

#### Desktop

<details>
    <summary>Click to expand!</summary>

Home view

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/desktop_home.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/00_home_view.yaml)

Home info

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/desktop_home_info.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/10_home_info_view.yaml)

System info

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/desktop_system_info.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/30_system_info_view.yaml)

Automations view

[![](https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/desktop_automations.jpg)](https://github.com/Limych/HomeAssistantConfiguration/blob/master/lovelace/00_automations_view.yaml)

</details>

## Add-ons

* [A better presence](https://github.com/helto4real/hassio-add-ons/tree/master/presence);
* [Backup Hass.io to Google Drive](https://github.com/samccauley/addon-hassiogooglebackup#readme);
* [Check Home Assistant Configuration](https://www.home-assistant.io/addons/check_config/) - official addon;
* [IDE](https://github.com/hassio-addons/addon-ide/blob/master/README.md);
* [Log Viewer](https://github.com/hassio-addons/addon-log-viewer);
* [MQTT Server & Web Client](https://github.com/hassio-addons/addon-mqtt/blob/master/README.md);
* [Samba Share](https://www.home-assistant.io/addons/samba/) - official addon;
