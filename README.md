# Rasberry pi, passive and active hamradio device.

![](https://www.distrelec.biz/Web/WebShopImages/landscape_large/3-/03/Raspberry%20Pi-RASPBERRY-PI-4-CASE-RW-30152783-03.jpg)

- https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit

- download lite version

- `dd if=file.img of=/dev/mmcblk0 bs=1M conv=fsync status=progress`

- mount `boot` partition and `touch ssh`

- mount `rootfs` partition and edit `/etc/dhcpcd.conf` to enable static IPv4.

- `ssh` to the device using user `pi` and password `raspberry` 

- Set `locale`:

  - ```bash
    # cat > /etc/default/locale
    LANG=en_US.UTF-8
    LC_NUMERIC=es_ES.UTF-8
    LC_TIME=es_ES.UTF-8
    LC_MONETARY=es_ES.UTF-8
    LC_PAPER=es_ES.UTF-8
    LC_NAME=es_ES.UTF-8
    LC_ADDRESS=es_ES.UTF-8
    LC_TELEPHONE=es_ES.UTF-8
    LC_MEASUREMENT=es_ES.UTF-8
    LC_IDENTIFICATION=es_ES.UTF-8
    ^EOF
    # locale-gen
    ```

- update it with `sudo apt update && sudo apt upgrade`

- `sudo raspi-config`

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
...
root@IOT-01-RASB:/home/taglio# apt autoremove
...
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

Install git:

```bash
# apt install git
```

Disable bluetooth and wireless:

```bash
# echo dtoverlay=disable-bt >> /boot/config.txt
# echo dtoverlay=pi3-disable-wifi >> /boot/config.txt
# systemctl disable bluetooth.service
# systemctl disable wpa_supplicant.service
```

Disable others services:

```
# systemctl disable avahi-daemon.service
```



Add your user and add your identity:

```bash
# useradd -m taglio
# for i in $(cat /etc/group | grep pi | sed /^pi.*/d | cut -d : -f1); do a+=$(printf "%s," $i); done
# eval usermod -G $(echo $a | sed "s|,$||") taglio 
# passwd taglio
# exit
taglio@trimurti:~/Bin$ ssh-copy-id -i /home/taglio/.ssh/id_ed25519.pub ham-01-rasb.red.ama
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/taglio/.ssh/id_ed25519.pub"
The authenticity of host 'ham-01-rasb.red.ama (172.16.18.254)' can't be established.
ECDSA key fingerprint is SHA256:RH32lmukVHv3SUcK/ninNAoKMXW8+swlWVJ4eb/ZVCY.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
taglio@ham-01-rasb.red.ama's password: 

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'ham-01-rasb.red.ama'"
and check to make sure that only the key(s) you wanted were added.

taglio@trimurti:~/Bin$
```

Delete pi user:

```bash
# userdel pi
# rm -rf /home/pi
```

#### External SB X-Fi Surround 5.1 Pro



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

#### Skywave Linux

![](https://github.com/redeltaglio/rasberry-hackrf/raw/main/Images/skywave.png)

To got a good work environment with all the libraries necessary and all the tools installed, I prefer using a [Linux distribution](https://distrowatch.com/) dedicated to radio ham. My choose is:

- [Skywave Linux](https://skywavelinux.com/)

This distribution doesn't got the need to be installed and with `qemu` or `virtualbox` we can run it without any problem. It use the [i3](https://i3wm.org/) [tiling window manager](https://en.wikipedia.org/wiki/Tiling_window_manager), you've got to understand how does it work, but it rocks!

