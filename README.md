# My Home Assistant Configuration

This [Home Assistant](https://www.home-assistant.io/) configuration is based on [configuration by Isabella Gross Alström](https://isabellaalstrom.github.io/).

![](https://img.shields.io/maintenance/yes/2019.svg?style=popout)
![](https://img.shields.io/github/last-commit/Limych/hassio-config.svg?style=popout)
![](https://img.shields.io/github/issues-raw/Limych/hassio-config.svg?label=Open%20todos&style=popout)
![](https://img.shields.io/github/issues-closed-raw/Limych/hassio-config.svg?colorB=green&label=Closed%20todos&style=popout)
![](https://img.shields.io/github/issues/Limych/hassio-config/bug.svg?colorB=red&label=Bugs&style=popout)

Like the Isabella I'm using the GitHub [issues](https://github.com/Limych/hassio-config/issues) and [project](https://github.com/Limych/hassio-config/projects/1) to keep track of bugs in my configuration and new features I want to make/use.

## Organizing the configuration

This configuration is broken down into [packages](https://www.home-assistant.io/docs/configuration/packages/), sort of mini configuration-files. This makes it easy to see everything pertaining to a specific implementation.

But while using packages you can no longer reload your config with the buttons in the ui.

## Ecosystem

Now I have very few devices in the system. But I plan to gradually add new ones.

Now I am running Hass.io on my FreeNAS server into Bhyve virtual machine which emulates Raspberry Pi 3 Model B+ 32bit.

1. Personal gadgets:
    1. Android devices (Phones and Tablets);
1. Media:
    1. Two [LinkPlay-driven](https://linkplay.com/) Wireless Speakers;
    1. [Emby](https://emby.media/) Media Server;
    1. [FreeNAS](https://freenas.org/) File Server;
1. Security:
    1. [Beward DS06M](https://www.beward.ru/katalog/ip-videodomofony/vyzyvnye-paneli/vyzyvnaya-panel-ds06m/) Doorbell;
    1. [OPNsense-driven](https://opnsense.org/) Network Firewall;
1. Climate:
    1. Home made [ESP32-driven](https://ru.wikipedia.org/wiki/ESP32) climate sensor (now only indoor Pressure, Humidity & Temperature);

## Lovelace

I'm using yaml mode, with includes.

My main Lovelace-file is found [here](https://github.com/Limych/hassio-config/blob/master/ui-lovelace.yaml), and my folder with includes [here](https://github.com/Limych/hassio-config/tree/master/lovelace). This is very much still a work in progress, so files might not correspond exactly to screenshots.

I put a lot of work into making this repo available and updated to inspire and help others!

### Examples from my Lovelace GUI

I have tried to make a GUI that is mobile first, since that's how I most often look at it.

Click on the images to get to the corresponding YAML-file.

#### Mobile

Home view

![](https://github.com/Limych/hassio-config/docs_images/mobile_home.jpg)

Home info

![](https://github.com/Limych/hassio-config/docs_images/mobile_home_info.jpg)

#### Desktop

Home view

![](https://github.com/Limych/hassio-config/docs_images/desktop_home.jpg)

Home info

![](https://github.com/Limych/hassio-config/docs_images/desktop_home_info.jpg)

## Add-ons

* [A better presence](https://github.com/helto4real/hassio-add-ons/tree/master/presence);
* [Backup Hass.io to Google Drive](https://github.com/samccauley/addon-hassiogooglebackup#readme);
* [Check Home Assistant Configuration](https://www.home-assistant.io/addons/check_config/) - official addon;
* [IDE](https://github.com/hassio-addons/addon-ide/blob/master/README.md);
* [Log Viewer](https://github.com/hassio-addons/addon-log-viewer);
* [MQTT Server & Web Client](https://github.com/hassio-addons/addon-mqtt/blob/master/README.md);
* [Samba Share](https://www.home-assistant.io/addons/samba/) - official addon;
