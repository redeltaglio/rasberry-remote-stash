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

1. `sudo apt install hackrf soapysdr-module-hackrf`

