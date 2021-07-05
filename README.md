# Rasberry pi, hackrf and soapy SDR

![](https://www.distrelec.biz/Web/WebShopImages/landscape_large/3-/03/Raspberry%20Pi-RASPBERRY-PI-4-CASE-RW-30152783-03.jpg)

1. https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit
2. download lite version
3. `dd if=file.img of=/dev/mmcblk0 bs=1M conv=fsync status=progress`
4. mount `boot` partition and `touch ssh`
5. mount `rootfs` partition and edit `/etc/dhcpcd.conf` to enable static IPv4.
6. `ssh` to the device using user `pi` and password `raspberry` 
7. update it with `sudo apt update && sudo apt upgrade`
8. `sudo raspi-config`

In case you are updating the hackrf one by remote remember that you can remove USB power using:

```shell
# disable external wake-up; do this only once
echo disabled > /sys/bus/usb/devices/usb1/power/wakeup 

echo on > /sys/bus/usb/devices/usb1/power/level       # turn on
echo suspend > /sys/bus/usb/devices/usb1/power/level  # turn off
```

#### Rasbian update

Rasbian is a Linux distribution and, as all the others, got it personal [cheat sheet](https://en.wikipedia.org/wiki/Cheat_sheet) to a correct administration.

```shell
root@IOT-01-RASB:/home/taglio# rpi-update 
 *** Raspberry Pi firmware updater by Hexxeh, enhanced by AndrewS and Dom
 *** Performing self-update
 *** Relaunching after update
 *** Raspberry Pi firmware updater by Hexxeh, enhanced by AndrewS and Dom
 *** We're running for the first time
 *** Backing up files (this will take a few minutes)
 *** Backing up firmware
 *** Backing up modules 5.10.17-v7+
#############################################################
WARNING: This update bumps to rpi-5.10.y linux tree
See: https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=288234
'rpi-update' should only be used if there is a specific
reason to do so - for example, a request by a Raspberry Pi
engineer or if you want to help the testing effort
and are comfortable with restoring if there are regressions.

DO NOT use 'rpi-update' as part of a regular update process.

##############################################################
Would you like to proceed? (y/N)

 *** Downloading specific firmware revision (this will take a few minutes)
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   168  100   168    0     0    126      0  0:00:01  0:00:01 --:--:--   126
100  120M  100  120M    0     0  1744k      0  0:01:10  0:01:10 --:--:-- 1920k
 *** Updating firmware
 *** Updating kernel modules
 *** depmod 5.10.46-v8+
 *** depmod 5.10.46-v7+
 *** depmod 5.10.46-v7l+
 *** depmod 5.10.46+
 *** Updating VideoCore libraries
 *** Using HardFP libraries
 *** Updating SDK
 *** Running ldconfig
 *** Storing current firmware revision
 *** Deleting downloaded files
 *** Syncing changes to disk
 *** If no errors appeared, your firmware was successfully updated to f29ab05611eef385d17675c77190df0b87a0d456
 *** A reboot is needed to activate the new firmware
root@IOT-01-RASB:/home/taglio# 

```

Then a reboot is needed and we can visualize the new installed firmware doing the classical:

```shell
taglio@IOT-01-RASB:~ $ uname -a
Linux IOT-01-RASB 5.10.46-v7+ #1432 SMP Fri Jul 2 21:16:37 BST 2021 armv7l GNU/Linux
taglio@IOT-01-RASB:~ $ 
```

Next:

```shell
root@IOT-01-RASB:/home/taglio# apt dist-upgrade
Reading package lists... Done
Building dependency tree       
Reading state information... Done
Calculating upgrade... Done
The following packages were automatically installed and are no longer required:
  lxplug-volume nyx python-colorzero python3-stem
Use 'sudo apt autoremove' to remove them.
The following NEW packages will be installed:
  gui-pkinst lxplug-volumepulse pi-printer-support printer-driver-escpr
The following packages will be upgraded:
  raspberrypi-ui-mods
1 upgraded, 4 newly installed, 0 to remove and 0 not upgraded.
Need to get 752 kB of archives.
After this operation, 897 kB of additional disk space will be used.
Do you want to continue? [Y/n] Y
Get:1 http://archive.raspberrypi.org/debian buster/main armhf gui-pkinst armhf 0.2 [127 kB]
Get:2 http://archive.raspberrypi.org/debian buster/main armhf lxplug-volumepulse armhf 0.5 [19.8 kB]
Get:3 http://archive.raspberrypi.org/debian buster/main armhf pi-printer-support all 1.1 [2,272 B]
Get:4 http://archive.raspberrypi.org/debian buster/main armhf printer-driver-escpr armhf 1.7.8-1~bpo10+1 [281 kB]
Get:5 http://archive.raspberrypi.org/debian buster/main armhf raspberrypi-ui-mods armhf 1.20201210+nmu1 [323 kB]
Fetched 752 kB in 5s (163 kB/s)               
Reading changelogs... Done
Selecting previously unselected package gui-pkinst.
(Reading database ... 202309 files and directories currently installed.)
Preparing to unpack .../gui-pkinst_0.2_armhf.deb ...
Unpacking gui-pkinst (0.2) ...
Selecting previously unselected package lxplug-volumepulse.
Preparing to unpack .../lxplug-volumepulse_0.5_armhf.deb ...
Unpacking lxplug-volumepulse (0.5) ...
Selecting previously unselected package pi-printer-support.
Preparing to unpack .../pi-printer-support_1.1_all.deb ...
Unpacking pi-printer-support (1.1) ...
Selecting previously unselected package printer-driver-escpr.
Preparing to unpack .../printer-driver-escpr_1.7.8-1~bpo10+1_armhf.deb ...
Unpacking printer-driver-escpr (1.7.8-1~bpo10+1) ...
Preparing to unpack .../raspberrypi-ui-mods_1.20201210+nmu1_armhf.deb ...
dpkg-query: package 'raspberrypi-ui-mods' is not installed
Use dpkg --contents (= dpkg-deb --contents) to list archive files contents.
Unpacking raspberrypi-ui-mods (1.20201210+nmu1) over (1.20200611) ...
Setting up lxplug-volumepulse (0.5) ...
Setting up printer-driver-escpr (1.7.8-1~bpo10+1) ...
Setting up gui-pkinst (0.2) ...
Setting up raspberrypi-ui-mods (1.20201210+nmu1) ...
Installing new version of config file /etc/xdg/lxpanel/LXDE-pi/panels/panel ...
Installing new version of config file /etc/xdg/openbox/lxde-pi-rc.xml ...
Adding user `root' to group `lpadmin' ...
Adding user root to group lpadmin
Done.
Adding user `pi' to group `lpadmin' ...
Adding user pi to group lpadmin
Done.
Adding user `taglio' to group `lpadmin' ...
Adding user taglio to group lpadmin
Done.
The desktop has been updated.
To apply the updates, please reboot your Pi, and then select one of the options on the Defaults page in Appearance Settings.
Setting up pi-printer-support (1.1) ...
Processing triggers for shared-mime-info (1.10-1) ...
Processing triggers for cups (2.2.10-6+deb10u4) ...
Updating PPD files for escpr ...
root@IOT-01-RASB:/home/taglio#
```

One good trick to pass from plain RaspiOS to RaspiOS-Lite in the case you've done a project error:

```shell
root@IOT-01-RASB:/home/taglio#  apt purge xserver* lightdm* raspberrypi-ui-mods
...
root@IOT-01-RASB:/home/taglio# apt autoremove
...
root@IOT-01-RASB:/home/taglio#
```



#### Hackrf one

![](https://upload.wikimedia.org/wikipedia/commons/0/0b/SDR_HackRF_one_PCB.jpg)

```shell
Bus 001 Device 003: ID 1d50:6089 OpenMoko, Inc. Great Scott Gadgets HackRF One SDR
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0 
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  idVendor           0x1d50 OpenMoko, Inc.
  idProduct          0x6089 Great Scott Gadgets HackRF One SDR
  bcdDevice            1.02
  iManufacturer           1 Great Scott Gadgets
  iProduct                2 HackRF One
  iSerial                 4 0000000000000000088869dc35694c1b
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0020
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          3 Transceiver
    bmAttributes         0x80
      (Bus Powered)
    MaxPower              500mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass       255 Vendor Specific Class
      bInterfaceSubClass    255 Vendor Specific Subclass
      bInterfaceProtocol    255 Vendor Specific Protocol
      iInterface              0 
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0200  1x 512 bytes
        bInterval               0
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x02  EP 2 OUT
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0200  1x 512 bytes
        bInterval               0
Device Qualifier (for other device speed):
  bLength                10
  bDescriptorType         6
  bcdUSB               2.00
  bDeviceClass            0 
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  bNumConfigurations      1
can't get debug descriptor: Resource temporarily unavailable
cannot read device status, Resource temporarily unavailable (11)

```

`sudo apt install hackrf soapysdr-module-hackrf`

Download from [mossmann hackrf github](https://github.com/mossmann/hackrf) the latest release.

```shell
pi@IOT-02-RASB:~/hackrf-2021.03.1 $ hackrf_info
hackrf_info version: unknown
libhackrf version: unknown (0.5)
Found HackRF
Index: 0
Serial number: 0000000000000000088869dc35694c1b
Board ID Number: 2 (HackRF One)
Firmware Version: 2018.01.1 (API:1.02)
Part ID Number: 0xa000cb3c 0x00614764
pi@IOT-02-RASB:~/hackrf-2021.03.1 $ 

```

Update the firmware:

```shell
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1/firmware-bin# hackrf_spiflash -w hackrf_one_usb.bin
File size 35444 bytes.
Erasing SPI flash.
Writing 35444 bytes at 0x000000.
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1/firmware-bin# 
```

Update the [CPLD](https://en.wikipedia.org/wiki/Complex_programmable_logic_device):

```shell
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1# hackrf_cpldjtag -x firmware/cpld/sgpio_if/default.xsvf
File size 37629 bytes.
LED1/2/3 blinking means CPLD program success.
LED3/RED steady means error.
Wait message 'Write finished' or in case of LED3/RED steady, Power OFF/Disconnect the HackRF.
Write finished.
Please Power OFF/Disconnect the HackRF.
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1#
```

#### Soapy remote

![](https://raw.githubusercontent.com/wiki/pothosware/SoapyRemote/images/soapy_sdr_remote_logo.png)

Use [instructions](https://github.com/pothosware/SoapyRemote/wiki) that you can find into the github.

```shell
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1# apt install soapyserver soapysdr-module-hackrf
Reading package lists... Done
Building dependency tree       
Reading state information... Done
The following package was automatically installed and is no longer required:
  python-colorzero
Use 'sudo apt autoremove' to remove it.
The following NEW packages will be installed:
  soapyremote-server
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Need to get 57.4 kB of archives.
After this operation, 171 kB of additional disk space will be used.
Get:1 http://mirrors.ircam.fr/pub/raspbian/raspbian buster/main armhf soapyremote-server armhf 0.4.3-1 [57.4 kB]
Fetched 57.4 kB in 1s (49.0 kB/s)          
Selecting previously unselected package soapyremote-server.
(Reading database ... 40387 files and directories currently installed.)
Preparing to unpack .../soapyremote-server_0.4.3-1_armhf.deb ...
Unpacking soapyremote-server (0.4.3-1) ...
Setting up soapyremote-server (0.4.3-1) ...
Created symlink /etc/systemd/system/SoapySDRServer.service → /lib/systemd/system/soapyremote-server.service.
Created symlink /etc/systemd/system/multi-user.target.wants/soapyremote-server.service → /lib/systemd/system/soapyremote-server.service.
Processing triggers for man-db (2.8.5-2) ...
root@IOT-02-RASB:/home/pi/hackrf-2021.03.1#
```

Connect using [CubicSDR](https://github.com/cjcliffe/CubicSDR) or others that support the Soapy server protocol.

#### CubicSDR

https://github.com/cjcliffe/CubicSDR/wiki/Build-Linux

