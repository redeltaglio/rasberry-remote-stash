# Rasberry pi, passive and active hamradio device.

![](https://www.distrelec.biz/Web/WebShopImages/landscape_large/3-/03/Raspberry%20Pi-RASPBERRY-PI-4-CASE-RW-30152783-03.jpg)

- https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit

- download lite version

- `dd if=file.img of=/dev/mmcblk0 bs=1M conv=fsync status=progress`

- mount `boot` partition and `touch ssh`

- mount `rootfs` partition and edit `/etc/dhcpcd.conf` to enable static IPv4.

- `ssh` to the device using user `pi` and password `raspberry` 

- Set `locale`:

  - `raspi-config`: Localization Options [`en_US.UTF-8`, `es_ES.UTF-8`] ; Timezone [`Europe/Madrid`]; 

    ```bash
    # cat > /etc/default/locale
    LANG=en_US.UTF-8
    LANGUAGE=en_US.UTF-8
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

  - set keyboard with: `localectl set-keymap es`

  - Reboot.

- update it with `sudo apt update && sudo apt upgrade`

- set the hostname: `sudo raspi-config`

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

Configure ssh to forward agent, identities and X11 to the HAM raspberry. Verify it:

```bash
taglio@trimurti:~$ cat /etc/ssh/ssh_config.d/ham.conf 
Host ham*
	AddKeysToAgent ask
	IdentityFile ~/.ssh/id_ed25519
	ForwardAgent yes
	ForwardX11 yes
	
taglio@trimurti:~$  ssh-add -L
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDGNNdXk7F17jGtt8xN51bR8toCET/my2mjQX4FkBVt8AwqEFoZg7AQcI9QReIyIOskiG7PXKD6YFk2bE5lc8QoHPeJCD1NHN/V0iflteeP4ZhtG/HH6NIGwEMsTsoxM8Uk4gU+kBWfFnmpRixXlCZjgKmRK0QdBdqX/0CVIDA0Z8ZO7W6dzXo+aje/kd/hD/T9jdAom0B+keXjaWRuZtIZ75v7hSBrG8K1azG9rvMX9zJHUwq8NXc7/ut90UGFFKvGgBt1kwc/Q1NiRbZujJ31+eKJJVXCp+IYl9SwVchl0FFQeR6ylWSO/rpt75yDgZYqpiTcdQ3lTbhX+rfUNX9veC7XJ6qTIoqP9kzUDZocSdNpLFOloor9LciGMJ1E7DJtqs7ZizlQVPRfOyP0EeO8Y9+JGUfQWOgb7w1OIsmJU54dFPVM20cxzsq71KOGS/LCvnqHl+UAhD6V+HSKkWpQCNbhk8q7IhjDqKEJ2LhfW2FHCANQJ7GyWRbVK/keHLk= taglio@telecom.lobby
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIZfNTAqRcC2VizgFX++yZLRAWaZi9iRMHuoVis4T38w taglio@telecom.lobby
taglio@trimurti:~$ 
```

Configure pam_ssh_agent_auth onto the HAM raspberry for password less operations with sudo:

```bash
# apt install libpam-ssh-agent-auth
# cp /home/taglio/.ssh/authorized_keys /etc/ssh/authorized_keys
# chown root:root /etc/ssh/authorized_keys ; chmod 0644 /etc/ssh/authorized_keys
```

Configure pam.d sudo file:

```bash
# cat /etc/pam.d/sudo
auth sufficient /usr/lib/arm-linux-gnueabihf/security/pam_ssh_agent_auth.so file=/etc/ssh/authorized_keys

@include common-auth
@include common-account
@include common-session-noninteractive
#
```

Configure and restart sshd:

```bash
# cat /etc/ssh/sshd_config
Include /etc/ssh/sshd_config.d/*.conf
AddressFamily inet
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM yes
AllowAgentForwarding yes
AllowTcpForwarding yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem	sftp	/usr/lib/openssh/sftp-server
# /etc/init.d/ssh restart
Restarting ssh (via systemctl): ssh.service.
#
```

Add ssh-add to login file read by bash shell:

```bash
$ echo ssh-add >> .profile
```

Delete pi user:

```bash
# userdel pi
# rm -rf /home/pi
```

Add fortune and uprecords to motd:

```bash
# cat /dev/null> /etc/motd
# apt install fortune uptimed
# rm /etc/profile.d/{sshpwd.sh,wifi-check.sh}
# echo 'echo " "'  > /etc/profile.d/00uptimed.sh
# echo "uprecords" >> /etc/profile.d/00uptimed.sh
# echo 'echo " "'  > /etc/profile.d/01fortune.sh
# echo "/usr/games/fortune -a" >> /etc/profile.d/01fortune.sh
```

#### External SB X-Fi Surround 5.1 Pro

![](https://github.com/redeltaglio/rasberry-hackrf/raw/main/Images/12.png)



Linux kernel driver and driver interface [API](https://en.wikipedia.org/wiki/API) is provided by [ALSA](https://en.wikipedia.org/wiki/Advanced_Linux_Sound_Architecture) software framework. It directly interact with hardware devices like our USB soundcard.

Blacklist the board card:

```bash
# echo blacklist snd_bcm2835 > /etc/modprobe.d/bcm2835.conf
# rmmod snd_bcm2835
```

Disable vn4 driver audio:

```bash
# sed -i "s|dtoverlay=vc4-kms-v3d|dtoverlay=vc4-kms-v3d,audio=off|" /boot/config.txt
# reboot
```

Verify:

```bash
taglio@HAM-01-RASPB:~ $ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 1: USB Audio [USB Audio #1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
taglio@HAM-01-RASPB:~ $ 
```

Card id is `1`.

Verify the kernel driver that manage the [SB X-Fi Surround 5.1 Pro](https://us.creative.com/p/archived-products/sound-blaster-x-fi-surround-5-1-pro):

```bash
taglio@HAM-01-RASB:~ $ cat /proc/asound/modules
 1 snd_usb_audio
taglio@HAM-01-RASB:~ $
```

Verify module options:

```bash
taglio@HAM-01-RASB:~ $ modinfo snd_usb_audio | grep -v alias
filename:       /lib/modules/5.15.24-v7+/kernel/sound/usb/snd-usb-audio.ko
license:        GPL
description:    USB Audio
author:         Takashi Iwai <tiwai@suse.de>
srcversion:     E73A30484EDD3D310F8DAB2
depends:        mc,snd-usbmidi-lib,snd-pcm,snd,snd-hwdep
intree:         Y
name:           snd_usb_audio
vermagic:       5.15.24-v7+ SMP mod_unload modversions ARMv7 p2v8 
parm:           index:Index value for the USB audio adapter. (array of int)
parm:           id:ID string for the USB audio adapter. (array of charp)
parm:           enable:Enable USB audio adapter. (array of bool)
parm:           vid:Vendor ID for the USB audio device. (array of int)
parm:           pid:Product ID for the USB audio device. (array of int)
parm:           device_setup:Specific device setup (if needed). (array of int)
parm:           ignore_ctl_error:Ignore errors from USB controller for mixer interfaces. (bool)
parm:           autoclock:Enable auto-clock selection for UAC2 devices (default: yes). (bool)
parm:           lowlatency:Enable low latency playback (default: yes). (bool)
parm:           delayed_register:Quirk for delayed registration, given by id:iface, e.g. 0123abcd:4. (array of charp)
parm:           implicit_fb:Apply generic implicit feedback sync mode. (array of bool)
parm:           quirk_flags:Driver quirk bit flags. (array of uint)
parm:           use_vmalloc:Use vmalloc for PCM intermediate buffers (default: yes). (bool)
parm:           skip_validation:Skip unit descriptor validation (default: no). (bool)
taglio@HAM-01-RASB:~ $ 
```

ALSA creates concepts about **ALSA Card** and **ALSA Device**. Card refers to the hardware that can have multiple capabilities like sending sound to a speaker or receiving sound from a microphone or from another source, in our case our stash.  

Therefore an ALSA Card will have one ALSA device to send sound and another to receive sound. This is why in the output of `aplay -l` we see that the program call `subdevices`. 

One system could have more than one card this is why ALSA use what is called the **ALSA Card id**. An id could by identified by an integer or a name.

A device is identified by the couple **ALSA Card id, ALSA Device id**; device id is always numeric.

ALSA applications works only at device level. Applications are also adressed with:

**ALSA interface:ALSA Card id, ALSA Device id**

ALSA interface is an access protocol that come with to interfaces built that are:

- **hw**, provides direct communication to the hardware device.
- **plughw**, provides translation from a standardized protocol to one which is supported by the device.

To find the ALSA Card id:

```bash
taglio@HAM-01-RASB:~ $ cat /proc/asound/cards
 1 [Pro            ]: USB-Audio - SB X-Fi Surround 5.1 Pro
                      Creative Technology Ltd SB X-Fi Surround 5.1 Pro at usb-3f980000.usb-1.2, full 
taglio@HAM-01-RASB:~ $ 
```

In our case of study we find the two numeric and letters ids:

- `1`
- `Pro`

To find the Devices created by ALSA kernel module:

```bash
taglio@HAM-01-RASB:~ $ ls -l /proc/asound/card*
-r--r--r--  1 root root 0 feb 21 22:33 /proc/asound/cards

/proc/asound/card1:
total 0
-r--r--r-- 1 root root 0 feb 21 22:41 id
dr-xr-xr-x 4 root root 0 feb 21 22:33 pcm0c
dr-xr-xr-x 4 root root 0 feb 21 22:33 pcm0p
dr-xr-xr-x 4 root root 0 feb 21 22:33 pcm1p
-r--r--r-- 1 root root 0 feb 21 22:41 stream0
-r--r--r-- 1 root root 0 feb 21 22:41 stream1
-r--r--r-- 1 root root 0 feb 21 22:41 usbbus
-r--r--r-- 1 root root 0 feb 21 22:41 usbid
-r--r--r-- 1 root root 0 feb 21 22:41 usbmixer
taglio@HAM-01-RASB:~ $ 

```

A **pcm** folder represent a device. **pcm[0-9]c** represent a capture device.  **pcm[0-9]p** represent a playback device. Be careful because in my understanding connected to a capture or playback device there could be more that one jack, female connector. 

![](https://bootlin.com/wp-content/uploads/2020/04/audio-input-1.png)

The acronym pcm refers to [pulse-code modulation](https://en.wikipedia.org/wiki/Pulse-code_modulation).

Our card has got 3 ALSA Devices, to identify the devices id do:

```bash
taglio@HAM-01-RASB:~ $ cat /proc/asound/card1/pcm0c/info 
card: 1
device: 0
subdevice: 0
stream: CAPTURE
id: USB Audio
name: USB Audio
subname: subdevice #0
class: 0
subclass: 0
subdevices_count: 1
subdevices_avail: 1
taglio@HAM-01-RASB:~ $ cat /proc/asound/card1/pcm0p/info 
card: 1
device: 0
subdevice: 0
stream: PLAYBACK
id: USB Audio
name: USB Audio
subname: subdevice #0
class: 0
subclass: 0
subdevices_count: 1
subdevices_avail: 1
taglio@HAM-01-RASB:~ $ cat /proc/asound/card1/pcm1p/info 
card: 1
device: 1
subdevice: 0
stream: PLAYBACK
id: USB Audio
name: USB Audio #1
subname: subdevice #0
class: 0
subclass: 0
subdevices_count: 1
subdevices_avail: 1
taglio@HAM-01-RASB:~ $ 

```

Playback device is to send and Capture is receive. But ALSA create a series of concept devices called Virtual Device, the differences are that a physical device got an hardware behind and that got an hardware address. Virtual Devices are addressed by name and are created by plugins. 

To list all hardware and virtual devices created by default use:

```bash
aglio@HAM-01-RASB:~ $ aplay -L
null
    Discard all samples (playback) or generate zero samples (capture)
lavrate
    Rate Converter Plugin Using Libav/FFmpeg Library
samplerate
    Rate Converter Plugin Using Samplerate Library
speexrate
    Rate Converter Plugin Using Speex Resampler
jack
    JACK Audio Connection Kit
oss
    Open Sound System
pulse
    PulseAudio Sound Server
upmix
    Plugin for channel upmix (4,6,8)
vdownmix
    Plugin for channel downmix (stereo) with a simple spacialization
default
softvol
hw:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    Direct hardware device without any conversions
hw:CARD=Pro,DEV=1
    SB X-Fi Surround 5.1 Pro, USB Audio #1
    Direct hardware device without any conversions
plughw:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    Hardware device with all software conversions
plughw:CARD=Pro,DEV=1
    SB X-Fi Surround 5.1 Pro, USB Audio #1
    Hardware device with all software conversions
sysdefault:CARD=Pro
    SB X-Fi Surround 5.1 Pro, USB Audio
    Default Audio Device
front:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    Front output / input
surround21:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    4.0 Surround output to Front and Rear speakers
surround41:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
iec958:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    IEC958 (S/PDIF) Digital Audio Output
iec958:CARD=Pro,DEV=1
    SB X-Fi Surround 5.1 Pro, USB Audio #1
    IEC958 (S/PDIF) Digital Audio Output
dmix:CARD=Pro,DEV=0
    SB X-Fi Surround 5.1 Pro, USB Audio
    Direct sample mixing device
dmix:CARD=Pro,DEV=1
    SB X-Fi Surround 5.1 Pro, USB Audio #1
    Direct sample mixing device
usbstream:CARD=Pro
    SB X-Fi Surround 5.1 Pro
    USB Stream Output
taglio@HAM-01-RASB:~ $ 

```

[ALSA Plugins](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html) that can be programmed are:

- [adpcm](https://en.wikipedia.org/wiki/Adaptive_differential_pulse-code_modulation): software encoder, quadrature encoding, from analog to digital.
- [alaw](https://en.wikipedia.org/wiki/A-law_algorithm): an algorithm to optimize a limited channel, a limited hardware for digitalization of analog signals.
- [asym](https://alsa.opensrc.org/Asym):  combines half-duplex PCM plugins like dsnoop and dmix into one full-duplex device.
- [copy](https://alsa.opensrc.org/Copy_(plugin)): copy [samples](https://en.wikipedia.org/wiki/Sampling_(signal_processing)) from a master PCM to a slave PCM.
- [dmix](https://alsa.opensrc.org/Dmix): provides for direct mixing of multiple streams.
- [dshare](https://alsa.opensrc.org/Dshare): provides sharing channels.
- [dsnoop](https://bootlin.com/blog/audio-multi-channel-routing-and-mixing-using-alsalib/): splits one capture stream to more.
- [file](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_file): stores contents of a PCM stream to file or pipes the stream to a command, and optionally uses an existing file as an input data source.

- [hooks](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_hooks): used to call some 'hook' function when this plugin is opened, modified or closed. Typically, it is used to change control values for a certain state specially for the PCM.
- [hw](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_hw): communicates directly with the ALSA kernel driver. It is a raw communication without any conversions.
- [iec958](https://en.wikipedia.org/wiki/S/PDIF)
- [jack](https://alsa.opensrc.org/Jack_(plugin)): redirect sampling from pcm to [jack audio server](https://jackaudio.org/).
- [ladspa](https://alsa.opensrc.org/Ladspa_(plugin)): use [ladspa](https://www.ladspa.org/) with ALSA applications. 
- [lfloat](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_lfloat): converts linear to float samples and float to linear samples from master linear<->float conversion PCM to given slave PCM.
- [linear](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_linear):  converts linear samples from master linear conversion PCM to given slave PCM.
- [mulaw](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_mulaw): converts [Mu-Law](https://en.wikipedia.org/wiki/%CE%9C-law_algorithm) samples to linear or linear to Mu-Law samples from master Mu-Law conversion PCM to given slave PCM.
- [multi](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_multi): onverts multiple streams to one.
- [null](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_null): discards contents of a PCM stream using `/dev/null` or creates a stream with zero samples. using `/dev/full`.
- [plug](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_plug): converts channels, rate and format on request.
- [rate](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_rate): converts a stream rate. The input and output formats must be linear.
- [route](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_route): converts channels and applies volume during the conversion. The format and rate must match for both of them.
- [share](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_share): converts multiple streams to one.
- [shm](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_shm): communicates with aserver via shared memory. It is a raw communication without any conversions, but it can be expected worse performance.
- [softvol](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm_plugins.html#pcm_plugins_softvol): applies the software volume attenuation. The format, rate and channels must match for both of source and destination.

At least some output from `alsa-info`:

```bash
!!Loaded sound module options
!!---------------------------

!!Module: snd_usb_audio
	autoclock : Y
	delayed_register : (null),(null),(null),(null),(null),(null),(null),(null)
	device_setup : 0,0,0,0,0,0,0,0
	enable : Y,Y,Y,Y,Y,Y,Y,Y
	id : (null),(null),(null),(null),(null),(null),(null),(null)
	ignore_ctl_error : N
	implicit_fb : N,N,N,N,N,N,N,N
	index : -2,-1,-1,-1,-1,-1,-1,-1
	lowlatency : Y
	pid : -1,-1,-1,-1,-1,-1,-1,-1
	quirk_alias : (null),(null),(null),(null),(null),(null),(null),(null)
	quirk_flags : 0,0,0,0,0,0,0,0
	skip_validation : N
	use_vmalloc : Y
	vid : -1,-1,-1,-1,-1,-1,-1,-1


!!USB Mixer information
!!---------------------
--startcollapse--

USB Mixer: usb_id=0x041e3263, ctrlif=0, ctlerr=0
Card: Creative Technology Ltd SB X-Fi Surround 5.1 Pro at usb-3f980000.usb-1.2, full 
--endcollapse--


!!ALSA Device nodes
!!-----------------

crw-rw---- 1 root audio 116, 32 Feb 21 17:12 /dev/snd/controlC1
crw-rw---- 1 root audio 116, 36 Feb 21 17:12 /dev/snd/hwC1D0
crw-rw---- 1 root audio 116, 56 Feb 21 17:12 /dev/snd/pcmC1D0c
crw-rw---- 1 root audio 116, 48 Feb 21 17:44 /dev/snd/pcmC1D0p
crw-rw---- 1 root audio 116, 49 Feb 21 17:12 /dev/snd/pcmC1D1p
crw-rw---- 1 root audio 116,  1 Feb 21 17:12 /dev/snd/seq
crw-rw---- 1 root audio 116, 33 Feb 21 17:12 /dev/snd/timer

/dev/snd/by-id:
total 0
drwxr-xr-x 2 root root  60 Feb 21 17:12 .
drwxr-xr-x 4 root root 220 Feb 21 17:12 ..
lrwxrwxrwx 1 root root  12 Feb 21 17:12 usb-Creative_Technology_Ltd_SB_X-Fi_Surround_5.1_Pro_000000BM-00 -> ../controlC1

/dev/snd/by-path:
total 0
drwxr-xr-x 2 root root  60 Feb 21 17:12 .
drwxr-xr-x 4 root root 220 Feb 21 17:12 ..
lrwxrwxrwx 1 root root  12 Feb 21 17:12 platform-3f980000.usb-usb-0:1.2:1.0 -> ../controlC1


!!Aplay/Arecord output
!!--------------------

APLAY

**** List of PLAYBACK Hardware Devices ****
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 1: USB Audio [USB Audio #1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

ARECORD

**** List of CAPTURE Hardware Devices ****
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

!!Amixer output
!!-------------

!!-------Mixer controls for card Pro

Card hw:1 'Pro'/'Creative Technology Ltd SB X-Fi Surround 5.1 Pro at usb-3f980000.usb-1.2, full '
  Mixer name	: 'USB Mixer'
  Components	: 'USB041e:3263'
  Controls      : 3
  Simple ctrls  : 0


!!Alsactl output
!!--------------

--startcollapse--
state.Pro {
	control.1 {
		iface PCM
		name 'Playback Channel Map'
		value.0 0
		value.1 0
		comment {
			access read
			type INTEGER
			count 2
			range '0 - 36'
		}
	}
	control.2 {
		iface PCM
		device 1
		name 'Playback Channel Map'
		value.0 0
		value.1 0
		comment {
			access read
			type INTEGER
			count 2
			range '0 - 36'
		}
	}
	control.3 {
		iface PCM
		name 'Capture Channel Map'
		value.0 0
		value.1 0
		comment {
			access read
			type INTEGER
			count 2
			range '0 - 36'
		}
	}
}
--endcollapse--
```

Edit .asoundrc to specify a software mixer because this usb soundcard doesn't have one:

```bash
pcm.!default {
    type            plug
    slave.pcm       "softvol"   #make use of softvol
}

pcm.softvol {
    type            softvol
    slave {
        pcm        "dmix"      #redirect the output to dmix (instead of "hw:0,0")
    }
    control {
        name        "Master"       #override the PCM slider to set the softvol volume level globally
        card        1
    }
}

```

Install pulseaudio:

```bash
# apt install pulseaudio
# usermod -a -G pulse,pulse-access taglio
```

#### Cross compile armv7l binaries using a x86_64 workstation

Various options regarding toolchains to do cross compiling for obvious timing reasons and hardware performances of the little ARM device.

- [Raspberry deprecated toolchain](https://github.com/raspberrypi/tools).
- [ARM toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads).
- [Linaro toolchain](http://releases.linaro.org/components/toolchain/binaries/).
- [Musl](https://musl.cc/), a toolchain develop from scratch focused into [static cross native compile](https://jensd.be/1126/linux/cross-compiling-for-arm-or-aarch64-on-debian-or-ubuntu). 
- [Debian / Ubuntu packages](https://wiki.debian.org/CrossToolchains).

But you can ever build your personal toolchain using:

- [Crosstool-NG](https://crosstool-ng.github.io/).
- [Buildroot](https://buildroot.org/).
- [Gentoo](https://www.gentoo.org/) [crossdev](https://wiki.gentoo.org/wiki/Cross_build_environment).

For now we choose to use package from workstation distribution:

```bash
taglio@trimurti:~/Work/redama/rasberry-hackrf$ cat /etc/lsb-release 
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=21.10
DISTRIB_CODENAME=impish
DISTRIB_DESCRIPTION="Ubuntu 21.10"
taglio@trimurti:~/Work/redama/rasberry-hackrf$ 

```

That is as we just show the Ubuntu release, but not a [LTS](https://ubuntu.com/blog/what-is-an-ubuntu-lts-release) so that with the [Linaro](https://linaro.org/) we could have problems. 

```bash
taglio@trimurti:~/Work/redama/rasberry-hackrf$ sudo apt install gcc-arm-linux-gnueabi binutils-arm-linux-gnueabi
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  cpp-11-arm-linux-gnueabi cpp-arm-linux-gnueabi gcc-11-arm-linux-gnueabi gcc-11-arm-linux-gnueabi-base gcc-11-cross-base libasan6-armel-cross libatomic1-armel-cross libc6-armel-cross libc6-dev-armel-cross libgcc-11-dev-armel-cross libgcc-s1-armel-cross libgomp1-armel-cross
  libstdc++6-armel-cross libubsan1-armel-cross linux-libc-dev-armel-cross
Suggested packages:
  binutils-doc gcc-11-locales cpp-doc gcc-11-doc flex bison gdb-arm-linux-gnueabi gcc-doc
The following NEW packages will be installed:
  binutils-arm-linux-gnueabi cpp-11-arm-linux-gnueabi cpp-arm-linux-gnueabi gcc-11-arm-linux-gnueabi gcc-11-arm-linux-gnueabi-base gcc-11-cross-base gcc-arm-linux-gnueabi libasan6-armel-cross libatomic1-armel-cross libc6-armel-cross libc6-dev-armel-cross libgcc-11-dev-armel-cross
  libgcc-s1-armel-cross libgomp1-armel-cross libstdc++6-armel-cross libubsan1-armel-cross linux-libc-dev-armel-cross
0 upgraded, 17 newly installed, 0 to remove and 2 not upgraded.
Need to get 127 MB of archives.
After this operation, 390 MB of additional disk space will be used.
Do you want to continue? [Y/n] Y
...
taglio@trimurti:~/Work/redama/rasberry-hackrf$
```

And we try to compile an "hello world" program in C language for the `armv7l` processor:

```bash
taglio@trimurti:~/Work/redama/rasberry-hackrf/C$ cat helloworld.c 
#include<stdio.h>
int main()
{
        printf("Hello World!\n");
        return 0;
}
taglio@trimurti:~/Work/redama/rasberry-hackrf/C$ arm-linux-gnueabi-gcc helloworld.c -o helloworld-arm -static
taglio@trimurti:~/Work/redama/rasberry-hackrf/C$ file helloworld-arm 
helloworld-arm: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), statically linked, BuildID[sha1]=55f5e32b52352bf9658ef8c48c05d6b257c02d54, for GNU/Linux 3.2.0, not stripped
taglio@trimurti:~/Work/redama/rasberry-hackrf/C$ scp helloworld-arm ham-01-rasb.red.ama:/home/taglio
helloworld-arm                                                                                                                                                                                                                                          100%  527KB   8.5MB/s   00:00    
taglio@trimurti:~/Work/redama/rasberry-hackrf/C$

taglio@HAM-01-RASB:~ $ ./helloworld-arm 
Hello World!
taglio@HAM-01-RASB:~ $ uname -m
armv7l
taglio@HAM-01-RASB:~ $ 

```

Next we prepare our workstation with the cross compile toolkit with the available packages:

```bash
taglio@trimurti:~$ sudo dpkg --add-architecture armhf
# echo deb \[arch=armhf\] http://ports.ubuntu.com/ubuntu-ports impish-updates main restricted universe multiverse >> /etc/apt/sources.list
# echo deb \[arch=armhf\] http://ports.ubuntu.com/ubuntu-ports impish-security main restricted universe multiverse >> /etc/apt/sources.list
# apt update
taglio@trimurti:~$  sudo apt install crossbuild-essential-armhf
```

Why we need cross compile?

Because we want to follow the cutting edge speaking about ours radio ham programs. Because we want to use a lot of programs, some heavy, that aren't included into the package repository of [RaspiOS](https://en.wikipedia.org/wiki/Raspberry_Pi_OS). Because, at least but not last, time compile directly into the arm device is very long and resources are limited. 

#### ALSA PCM capture to network

![](https://roc-streaming.org/logo.png)

So what we want to obtain is the sound from a stash connected from the headphone jack to the line input jack, the blue one, transmitted to an IP network. We want to use X11 applications within an ssh remote session forwarding them and listen to them. To real scope of this document is build various radio ham remote stash, point of presence, and use the as we're directly interact with them.

Some application will work with audio servers and not directly with ALSA so we have to archive streaming over IP network for various scenario. 

We decide to use [ROC toolkit](https://roc-streaming.org/), because we've got different scenario and because we've found another [radio operator](https://grundstil.de/n3rd/ham) that use it.

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

