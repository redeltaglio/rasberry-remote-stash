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



