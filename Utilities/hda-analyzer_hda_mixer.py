#!/usr/bin/env python
#
# Copyright (c) 2008-2010 by Jaroslav Kysela <perex@perex.cz>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

import os
import struct
from fcntl import ioctl

def __ioctl_val1(val):
  # workaround for OverFlow bug in python 2.4
  if val & 0x80000000:
    return -((val^0xffffffff)+1)
  return val

CTL_IOCTL_CARD_INFO = __ioctl_val1(0x81785501)
CTL_IOCTL_ELEM_INFO = __ioctl_val1(0xc1105511)
CTL_IOCTL_ELEM_READ = __ioctl_val1(0xc4c85512)
CTL_IOCTL_ELEM_WRITE = __ioctl_val1(0xc4c85513)

CTL_ELEM_TYPE_BOOLEAN = 1
CTL_ELEM_TYPE_INTEGER = 2
CTL_ELEM_TYPE_ENUMERATED = 3
CTL_ELEM_TYPE_BYTES = 4
CTL_ELEM_TYPE_IEC958 = 5
CTL_ELEM_TYPE_INTEGER64 = 6

CTL_ELEM_TYPEs = {
  'boolean': CTL_ELEM_TYPE_BOOLEAN,
  'integer': CTL_ELEM_TYPE_INTEGER,
  'enumerated': CTL_ELEM_TYPE_ENUMERATED,
  'bytes':CTL_ELEM_TYPE_BYTES,
  'iec958':CTL_ELEM_TYPE_IEC958,
  'integer64':CTL_ELEM_TYPE_INTEGER64
}
CTL_ELEM_RTYPEs = {}
for i in CTL_ELEM_TYPEs:
  CTL_ELEM_RTYPEs[CTL_ELEM_TYPEs[i]] = i

CTL_ELEM_IFACE_CARD = 0
CTL_ELEM_IFACE_MIXER = 2
CTL_ELEM_IFACE_PCM = 3
CTL_ELEM_IFACEs = {
  "card": 0,
  "mixer": 2,
  "pcm": 3
}
CTL_ELEM_RIFACEs = {}
for i in CTL_ELEM_IFACEs:
  CTL_ELEM_RIFACEs[CTL_ELEM_IFACEs[i]] = i

CTL_ELEM_ACCESS_READ = (1<<0)
CTL_ELEM_ACCESS_WRITE = (1<<1)
CTL_ELEM_ACCESS_VOLATILE = (1<<2)
CTL_ELEM_ACCESS_TIMESTAMP = (1<<3)
CTL_ELEM_ACCESS_TLV_READ = (1<<4)
CTL_ELEM_ACCESS_TLV_WRITE = (1<<5)
CTL_ELEM_ACCESS_TLV_COMMAND = (1<<6)
CTL_ELEM_ACCESS_INACTIVE = (1<<8)
CTL_ELEM_ACCESS_LOCK = (1<<9)
CTL_ELEM_ACCESS_OWNER = (1<<10)

CTL_ELEM_ACCESSs = {
  'read': CTL_ELEM_ACCESS_READ,
  'write': CTL_ELEM_ACCESS_WRITE,
  'volatile': CTL_ELEM_ACCESS_VOLATILE,
  'timestamp': CTL_ELEM_ACCESS_TIMESTAMP,
  'tlv_read': CTL_ELEM_ACCESS_TLV_READ,
  'tlv_write': CTL_ELEM_ACCESS_TLV_WRITE,
  'tlv_command': CTL_ELEM_ACCESS_TLV_COMMAND,
  'inactive': CTL_ELEM_ACCESS_INACTIVE,
  'lock': CTL_ELEM_ACCESS_LOCK,
  'owner': CTL_ELEM_ACCESS_OWNER
}

UINTSIZE = len(struct.pack("I", 0))
LONGSIZE = len(struct.pack("l", 0))
LONGLONGSIZE = len(struct.pack("q", 0))

class AlsaMixerElemId:

  def __init__(self,
               numid=0,
               iface=CTL_ELEM_IFACE_MIXER,
               device=0,
               subdevice=0,
               name=None,
               index=0):
    self.numid = numid
    if type(iface) == type(''):
      self.iface = CTL_ELEM_IFACEs[iface]
    else:
      self.iface = iface is None and CTL_ELEM_IFACE_MIXER or iface
    self.device = device
    self.subdevice = subdevice
    self.name = name
    self.index = index
    self.binsize = len(self.pack())

  def pack(self):
    return struct.pack('IiII44sI',
                self.numid, self.iface, self.device, self.subdevice,
                self.name, self.index)

  def unpack(self, binid):
    self.numid, self.iface, self.device, self.subdevice, \
      self.name, self.index = struct.unpack('IiII44sI', binid)
    self.name = self.name.replace('\x00', '')

  def get_text_info(self):
    return 'iface="%s",name="%s",index=%s,device=%s,subdevice=%s' % \
      (CTL_ELEM_RIFACEs[self.iface], self.name, self.index,
      self.device, self.subdevice)

class AlsaMixerElem:

  def __init__(self, mixer, id):
    self.mixer = mixer
    self.id = id
    info = self.__info()
    self.type = info['type']
    self.stype = CTL_ELEM_RTYPEs[self.type]
    self.access = info['access']
    self.count = info['count']
    self.owner = info['owner']
    if info['type'] in [CTL_ELEM_TYPE_INTEGER, CTL_ELEM_TYPE_INTEGER64]:
      self.min = info['min']
      self.max = info['max']
      self.step = info['step']
    elif info['type'] == CTL_ELEM_TYPE_ENUMERATED:
      self.items = info['items']
    self.dimen = info['dimen']
  
  def __info(self):
    bin = self.id.pack()+struct.pack('iIIi128s8s64s', 0, 0, 0, 0, '', '', '')
    res = ioctl(self.mixer.fd, CTL_IOCTL_ELEM_INFO, bin)
    self.id.unpack(res[:self.id.binsize])
    a = struct.unpack('iIIi128s8s64s', res[self.id.binsize:])
    b = {}
    b['id'] = self.id
    b['type'] = a[0]
    b['access'] = []
    for i in CTL_ELEM_ACCESSs:
      if CTL_ELEM_ACCESSs[i] & a[1]:
        b['access'].append(i)
    b['count'] = a[2]
    b['owner'] = a[3]
    if b['type'] == CTL_ELEM_TYPE_INTEGER:
      b['min'], b['max'], b['step'] = \
                      struct.unpack("lll", a[4][:LONGSIZE*3])
    elif b['type'] == CTL_ELEM_TYPE_INTEGER64:
      b['min'], b['max'], b['step'] = \
                      struct.unpack("qqq", a[4][:LONGLONGSIZE*3])
    elif b['type'] == CTL_ELEM_TYPE_ENUMERATED:
      b['items'], b['item'], b['name'] = \
                      struct.unpack("II64s", a[4][:UINTSIZE*2+64])
    b['dimen'] = struct.unpack("HHHH", a[5])
    return b

  def read(self):
    bin = self.id.pack() + struct.pack('I512s128s', 0, '', '')
    startoff = self.id.binsize + UINTSIZE
    if LONGSIZE == 8:
      bin += '\x00\x00\x00\x00'
      startoff += 4
    res = ioctl(self.mixer.fd, CTL_IOCTL_ELEM_READ, bin)
    if self.type == CTL_ELEM_TYPE_BOOLEAN:
      return map(lambda x: x != 0, struct.unpack("l"*self.count, res[startoff:startoff+self.count*LONGSIZE]))
    elif self.type == CTL_ELEM_TYPE_INTEGER:
      return struct.unpack("l"*self.count, res[startoff:startoff+self.count*LONGSIZE])
    elif self.type == CTL_ELEM_TYPE_INTEGER64:
      return struct.unpack("q"*self.count, res[startoff:startoff+self.count*LONGLONGSIZE])
    elif self.type == CTL_ELEM_TYPE_ENUMERATED:
      return struct.unpack("I"*self.count, res[startoff:startoff+self.count*UINTSIZE])
    elif self.type == CTL_ELEM_TYPE_BYTES:
      return res[startoff:startoff+self.count]
    else:
      raise ValueError, "Unsupported type %s" % CTL_ELEM_RTYPEs[self.type]

  def get_text_info(self, idx=None):
    res = self.id.get_text_info() + '\n'
    res += '  type="%s",access=%s,count=%s,owner=%s,dimen=%s\n' % \
      (self.stype, repr(self.access), self.count, self.owner, self.dimen)
    if self.stype.startswith('integer'):
      res += '  min=%s,max=%s,step=%s\n' % (self.min, self.max, self.step)
    elif self.stype == 'enumerated':
      res += '  items=%s\n' % (self.items)
    return res
    
class AlsaMixer:

  def __init__(self, card, ctl_fd=None):
    self.card = card
    if ctl_fd is None:
      self.fd = os.open("/dev/snd/controlC%s" % card, os.O_RDONLY)
    else:
      self.fd = os.dup(ctl_fd)

  def __del__(self):
    if not self.fd is None:
      os.close(self.fd)

if __name__ == '__main__':
  mixer = AlsaMixer(0)
  elem = AlsaMixerElem(mixer, AlsaMixerElemId(name="Mic Boost"))
  print elem.read()
  elem = AlsaMixerElem(mixer, AlsaMixerElemId(name="Capture Volume"))
  print elem.read()
