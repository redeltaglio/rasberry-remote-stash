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
