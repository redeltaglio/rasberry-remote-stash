#!/usr/bin/env python
#
# Copyright (c) 2008-2012 by Jaroslav Kysela <perex@perex.cz>
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

from hda_codec import *

SET_VERBS = {
  VERBS['SET_SDI_SELECT']: VERBS['GET_SDI_SELECT'],
  VERBS['SET_PIN_WIDGET_CONTROL']: VERBS['GET_PIN_WIDGET_CONTROL'],
  VERBS['SET_CONNECT_SEL']: VERBS['GET_CONNECT_SEL'],
  VERBS['SET_EAPD_BTLENABLE']: VERBS['GET_EAPD_BTLENABLE'],
  VERBS['SET_POWER_STATE']: VERBS['GET_POWER_STATE'],
}

def DecodeProcFile(proc_file):
  if len(proc_file) < 256:
    fd = open(proc_file)
  proc_file = fd.read(1024*1024)
  fd.close()
  if proc_file.find('Subsystem Id:') < 0:
      p = None
      try:
        from gzip import GzipFile
        from StringIO import StringIO
        s = StringIO(proc_file)
        gz = GzipFile(mode='r', fileobj=s)
        p = gz.read(1024*1024)
        gz.close()
      except:
        pass
      if p is None:
        try:
          from bz2 import decompress
          p = decompress(proc_file)
        except:
          pass
      if not p is None:
        proc_file = p
  return proc_file

def DecodeAlsaInfoFile(proc_file):
  if proc_file.find("ALSA Information Script") < 0:
    return [proc_file]
  pos = proc_file.find('HDA-Intel Codec information')
  if pos < 0:
    return [proc_file]
  proc_file = proc_file[pos:]
  pos = proc_file.find('--startcollapse--')
  proc_file = proc_file[pos+18:]
  pos = proc_file.find('--endcollapse--')
  proc_file = proc_file[:pos]
  res = []
  while 1:
    pos = proc_file.find('\nCodec: ')
    if pos < 0:
      break
    proc_file = proc_file[pos:]
    pos = proc_file[1:].find('\nCodec: ')
    if pos < 0:
      pos = len(proc_file)-2
    res.append(proc_file[:pos+2])
    proc_file = proc_file[pos:]
  return res

class HDACardProc:

  def __init__(self, card):
    self.card = card
    self.id = 'ProcId'
    self.driver = 'ProcDriver'
    self.name = 'ProcName'
    self.longname = 'ProcLongName'
    self.components = 'ProcComponents'

class HDABaseProc:

  delim = ' "[],:*'

  def decodestrw(self, str, prefix):
    if str.startswith(prefix):
      res = str[len(prefix):].strip()
      delim = self.delim
      if res[0] == '"':
        res = res[1:]
        delim = '"'
      rem = res
      for a in delim:
        pos = res.find(a)
        if pos >= 0:
          if rem == res:
            rem = rem[pos:]
          res = res[:pos]
      if rem == res:
        rem = ''
      ok = True
      while ok:
        ok = False
        for a in self.delim:
          if rem and rem[0] == a:
            rem = rem[1:]
            ok = True
      return rem.strip(), res.strip()
    self.wrongfile('string decode %s' % repr(str))

  def decodeintw(self, str, prefix='', forcehex=False):
    if str.startswith(prefix):
      res = str[len(prefix):].strip()
      rem = res
      for a in self.delim:
        pos = res.find(a)
        if pos >= 0:
          if rem == res:
            rem = rem[pos:]
          res = res[:pos]
      if rem == res:
        rem = ''
      ok = True
      while ok:
        ok = False
        for a in self.delim:
          if rem and rem[0] == a:
            rem = rem[1:]
            ok = True
      if res and forcehex:
        if not res.startswith('0x'):
          res = '0x' + res
      if res.startswith('0x'):
        return rem.strip(), int(res[2:], 16)
      return rem.strip(), int(res)
    self.wrongfile('integer decode %s (%s)' % (repr(str), repr(prefix)))

  def wrongfile(self, msg=''):
    raise ValueError, "wrong proc file format (%s)" % msg

class HDApcmDevice:

  def __init__(self, name, type, device):
    self.name = name
    self.type = type
    self.device = device

  def dump_extra(self):
    return '  Device: name="%s", type="%s", device=%s\n' % (self.name, self.type, self.device)

class HDApcmControl:

  def __init__(self, iface, name, index, device):
    self.iface = iface
    self.name = name
    self.index = index
    self.device = device
    self.amp_chs = None

  def dump_extra(self):
    str = '  Control: %sname="%s", index=%s, device=%s\n' % (self.iface and ("iface=\"%s\", " % self.iface) or "", self.name, self.index, self.device)
    if not self.amp_chs is None:
      str += '    ControlAmp: chs=%s, dir=%s, idx=%s, ofs=%s\n' % (self.amp_chs, self.amp_dir, self.amp_idx, self.amp_ofs)
    return str

  def amp_index_match(self, idx):
    if not self.amp_chs is None:
      count = (self.amp_chs & 1) + ((self.amp_chs >> 1) & 1)
      return idx >= self.amp_idx and idx < self.amp_idx + count
    else:
      return False

class ProcNode(HDABaseProc):

  def __init__(self, codec, nid, wcaps):
    self.codec = codec
    codec.proc_nids[nid] = self
    self.nid = nid
    self.wcaps = wcaps
    self.wtype = (self.wcaps >> 20) & 0x0f
    self.wtype_id = WIDGET_TYPE_IDS[self.wtype]
    self.device = None
    self.amp_vals = [[], []]
    self.connections = []
    self.params = {}
    self.verbs = {}
    self.controls = []
    if wcaps & (1 << 6):
      self.add_param(PARAMS['PROC_CAP'], 0)
    if wcaps & (1 << 7):
      self.add_verb(VERBS['GET_UNSOLICITED_RESPONSE'], 0)
    if wcaps & (1 << 9):
      self.add_verb(VERBS['GET_DIGI_CONVERT_1'], 0)
    if wcaps & (1 << 10):
      self.add_param(PARAMS['POWER_STATE'], 0)
    if self.wtype_id in ['AUD_IN', 'AUD_OUT']:
      self.add_verb(VERBS['GET_CONV' ], 0)
    if self.wtype_id == 'AUD_IN':
      self.add_verb(VERBS['GET_SDI_SELECT'], 0)

  def rw(self, verb, param):
    if verb in self.verbs:
      return self.verbs[verb]
    elif verb == VERBS['GET_CONNECT_LIST']:
      f1 = self.connections[param]
      f2 = 0
      if param + 1 < len(self.connections):
        f2 = self.connections[param+1]
      return f1 | (f2 << 16)
    elif verb == VERBS['GET_AMP_GAIN_MUTE']:
      dir = param & (1<<15) and HDA_OUTPUT or HDA_INPUT
      idx = param & (1<<13) and 1 or 0
      val = param & 0x7f
      if val >= len(self.amp_vals[dir]):
        print "AMP index out of range (%s >= %s)" % (val, len(self.amp_vals[dir]))
        while val >= len(self.amp_vals[dir]):
          self.amp_vals[dir].append([128, 128])
      return self.amp_vals[dir][val][idx]
    elif verb == VERBS['SET_AMP_GAIN_MUTE']:
      dir = param & (1<<15) and HDA_OUTPUT or HDA_INPUT
      idx = (param >> 8) & 0x0f
      if param & (1<<12):
        self.amp_vals[dir][idx][0] = param & 0xff
      if param & (1<<13) and len(self.amp_vals[dir][idx]) > 1:
        self.amp_vals[dir][idx][1] = param & 0xff
      return param
    elif verb == VERBS['SET_DIGI_CONVERT_1']:
      self.verbs[VERBS['GET_DIGI_CONVERT_1']] &= ~0xff
      self.verbs[VERBS['GET_DIGI_CONVERT_1']] |= param & 0xff
      return param
    elif verb == VERBS['SET_DIGI_CONVERT_2']:
      self.verbs[VERBS['GET_DIGI_CONVERT_1']] &= ~0xff00
      self.verbs[VERBS['GET_DIGI_CONVERT_1']] |= (param & 0xff) << 8
      return param
    elif verb in SET_VERBS:
      self.verbs[SET_VERBS[verb]] = param
      return param
    raise ValueError, "unimplemented node rw (0x%x, 0x%x, 0x%x)" % (self.nid, verb, param)

  def param_read(self, param):
    if param in self.params:
      return self.params[param]
    elif param == PARAMS['CONNLIST_LEN']:
      return len(self.connections) + (1 << 7)	# use long format
    raise ValueError, "unimplemented node param read (0x%x, 0x%x)" % (self.nid, param)

  def add_verb(self, verb, param, do_or=False):
    if do_or and verb in self.verbs:
      self.verbs[verb] |= param
    else:
      self.verbs[verb] = param

  def add_param(self, param, value):
    self.params[param] = value

  def add_device(self, line):
    line, name = self.decodestrw(line, 'name=')
    line, type = self.decodestrw(line, 'type=')
    line, device = self.decodeintw(line, 'device=')
    if self.device:
      self.wrongfile('more than one PCM device?')
    self.device = HDApcmDevice(name, type, device)

  def get_device(self):
    return self.device

  def add_converter(self, line):
    line, stream = self.decodeintw(line, 'stream=')
    line, channel = self.decodeintw(line, 'channel=')
    self.add_verb(VERBS['GET_CONV'],
                    ((stream & 0x0f) << 4) | (channel & 0x0f))

  def add_digital(self, line):
    bits = {
      'Enabled': DIG1_BITS['ENABLE'],
      'Validity': DIG1_BITS['VALIDITY'],
      'ValidityCfg': DIG1_BITS['VALIDITYCFG'],
      'Preemphasis': DIG1_BITS['EMPHASIS'],
      'Copyright': DIG1_BITS['COPYRIGHT'], # old buggy format
      'Non-Copyright': DIG1_BITS['COPYRIGHT'],
      'Non-Audio': DIG1_BITS['NONAUDIO'],
      'Pro': DIG1_BITS['PROFESSIONAL'],
      'GenLevel': DIG1_BITS['LEVEL'],
      'KAE' : -1 # ignore, so far
    }
    xbits = 0
    a = line.split(' ')
    for b in a:
      b = b.strip()
      if not b:
        return
      if not b in bits:
        self.wrongfile('unknown dig1 bit %s' % repr(b))
      if bits[b] >= 0:
        xbits |= 1 << bits[b]
    self.add_verb(VERBS['GET_DIGI_CONVERT_1'], xbits)

  def add_digitalcategory(self, line):
    line, res = self.decodeintw(line)
    self.add_verb(VERBS['GET_DIGI_CONVERT_1'], (res & 0x7f) << 8, do_or=True)

  def add_sdiselect(self, line):
    line, res = self.decodeintw(line)
    self.add_verb(VERBS['GET_SDI_SELECT'], res)

  def add_pcm(self, line1, line2, line3):
    line1, tmp1 = self.decodeintw(line1, '    rates [')
    line2, tmp2 = self.decodeintw(line2, '    bits [')
    self.add_param(PARAMS['PCM'],
              (tmp1 & 0xffff) | ((tmp2 & 0xffff) << 16))
    line3, tmp1 = self.decodeintw(line3, '    formats [')
    self.add_param(PARAMS['STREAM'], tmp1)

  def add_control(self, line):
    iface = None
    if line.find('iface=') > 0:
      line, iface = self.decodestrw(line, 'iface=')
    line, name = self.decodestrw(line, 'name=')
    line, index = self.decodeintw(line, 'index=')
    line, device = self.decodeintw(line, 'device=')
    self.controls.append(HDApcmControl(iface, name, index, device))

  def add_controlamp(self, line):
    ctl = self.controls[-1]
    line, ctl.amp_chs = self.decodeintw(line, 'chs=')
    line, ctl.amp_dir = self.decodestrw(line, 'dir=')
    line, ctl.amp_idx = self.decodeintw(line, 'idx=')
    line, ctl.amp_ofs = self.decodeintw(line, 'ofs=')
    ctl.amp_dir = ctl.amp_dir == 'In' and HDA_INPUT or HDA_OUTPUT

  def get_controls(self):
    return self.controls

  def add_ampcaps(self, line, dir):
    line = line.strip()
    par = PARAMS[dir == HDA_INPUT and 'AMP_IN_CAP' or 'AMP_OUT_CAP']
    if line == 'N/A':
      self.add_param(par, 0)
      return
    line, ofs = self.decodeintw(line, 'ofs=')
    line, nsteps = self.decodeintw(line, 'nsteps=')
    line, stepsize = self.decodeintw(line, 'stepsize=')
    line, mute = self.decodeintw(line, 'mute=')
    self.add_param(par,
               (ofs & 0x7f) | ((nsteps & 0x7f) << 8) | \
               ((stepsize & 0x7f) << 16) | ((mute & 1) << 31))

  def add_ampvals(self, line, dir):
    line = line.strip()
    self.amp_vals[dir] = []
    while len(line):
      if not line[0] == '[':
        self.wrongfile('amp vals [')
      pos = line.find(']')
      if pos <= 0:
        self.wrongfile('amp vals ]')
      str = line[1:pos]
      line = line[len(str)+2:].strip()
      val = []
      while str.startswith('0x'):
        str, val1 = self.decodeintw(str)
        val.append(val1)
      self.amp_vals[dir].append(val)

  def add_connection(self, line, conn):
    line, count = self.decodeintw(line)
    if count == -22:	# driver was not able to read connections
      count = 0
    res = 0
    if conn.startswith('    '):
      conn = conn.strip()
      res = 1
    else:
      conn = ''
    conns = []
    sel = -1
    while len(conn):
      if len(conn) > 4 and conn[4] == '*':
        sel = len(conns)
      conn, val = self.decodeintw(conn)
      conns.append(val)
    if count != len(conns):
      self.wrongfile('connections %s != %s' % (count, len(conns)))
    self.connections = conns
    self.add_verb(VERBS['GET_CONNECT_SEL'], sel)
    return res
    
  def add_unsolicited(self, line):
    line, tag = self.decodeintw(line, 'tag=', forcehex=True)
    line, enabled = self.decodeintw(line, 'enabled=')
    self.add_verb(VERBS['GET_UNSOLICITED_RESPONSE'],
                    (tag & 0x3f) | ((enabled & 1) << 7))

  def add_pincap(self, line):
    line = line.strip()
    # workaround for bad 0x08%x format string in hda_proc.c
    a = line.split(':')
    if line.startswith('0x08') and len(a[0]) != 10:
      line = "0x" + line[4:]
    line, tmp1 = self.decodeintw(line, '')
    self.add_param(PARAMS['PIN_CAP'], tmp1)

  def add_pindefault(self, line):
    line, tmp1 = self.decodeintw(line, '')
    self.add_verb(VERBS['GET_CONFIG_DEFAULT'], tmp1)

  def add_pinctls(self, line):
    line, tmp1 = self.decodeintw(line, '')
    self.add_verb(VERBS['GET_PIN_WIDGET_CONTROL'], tmp1)

  def add_eapd(self, line):
    line, tmp1 = self.decodeintw(line, '')
    self.add_verb(VERBS['GET_EAPD_BTLENABLE'], tmp1)

  def add_power(self, line):
    line, setting = self.decodestrw(line, 'setting=')
    line, actual = self.decodestrw(line, 'actual=')
    if setting in POWER_STATES:
      setting = POWER_STATES.index(setting)
    else:
      self.wrongfile('power setting %s' % setting)
    if actual in POWER_STATES:
      actual = POWER_STATES.index(actual)
    else:
      self.wrongfile('power actual %s' % actual)
    self.add_verb(VERBS['GET_POWER_STATE'], (setting & 0x0f) | ((actual & 0x0f) << 4))
  
  def add_powerstates(self, line):
    a = line.strip().split(' ')
    tmp1 = 0
    for b in a:
      if b in POWER_STATES:
        tmp1 |= 1 << POWER_STATES.index(b)
    self.add_param(PARAMS['POWER_STATE'], tmp1)

  def add_processcaps(self, line):
    line, benign = self.decodeintw(line, 'benign=')
    line, ncoeff = self.decodeintw(line, 'ncoeff=')
    self.add_param(PARAMS['PROC_CAP'],
                    (benign & 1) | ((ncoeff & 0xff) << 8))
  
  def add_processcoef(self, line):
    line, coef = self.decodeintw(line, '')
    self.add_verb(VERBS['GET_PROC_COEF'], coef)

  def add_processindex(self, line):
    line, idx = self.decodeintw(line, '')
    self.add_verb(VERBS['GET_COEF_INDEX'], idx)

  def add_volknob(self, line):
    line, delta = self.decodeintw(line, 'delta=')
    line, steps = self.decodeintw(line, 'steps=')
    line, direct = self.decodeintw(line, 'direct=')
    line, val = self.decodeintw(line, 'val=')
    self.add_param(PARAMS['VOL_KNB_CAP'], ((delta & 1) << 7) | (steps & 0x7f))
    self.add_verb(VERBS['GET_VOLUME_KNOB_CONTROL'], ((direct & 1) << 7) | (val & 0x7f))

  def dump_extra(self):
    str = ''
    if self.device:
      str += self.device.dump_extra()
    for c in self.controls:
      str += c.dump_extra()
    return str

class HDACodecProc(HDACodec, HDABaseProc):

  def __init__(self, card, device, proc_file):
    self.hwaccess = False
    self.fd = None
    self.proc_codec = None
    self.card = card
    self.device = device
    self.mcard = HDACardProc(card)
    self.proc_codec_id = None
    self.mixer = None
    self.parse(proc_file)
    if self.proc_codec_id:
      self.mcard.name = self.proc_codec_id

  def parse(self, str):

    def lookfor(idx, prefix):
      while idx < len(lines) and not lines[idx].startswith(prefix):
        idx += 1
      if idx >= len(lines):
        return idx, None
      idx += 1
      return idx, lines[idx-1][len(prefix):].strip()

    def lookforint(idx, prefix):
      idx, res = lookfor(idx, prefix)
      if res:
        if res.startswith('0x'):
          return idx, int(res[2:], 16)
        return idx, int(res)

    def decodeint(idx, prefix):
      str, res = self.decodeintw(lines[idx], prefix)
      return idx+1, res

    def decodefcnid(idx, prefix):
      if lines[idx].startswith(prefix):
        str, res = self.decodeintw(lines[idx][len(prefix):])
        if str.startswith('(unsol '):
          str, res1 = self.decodeintw(str[:-1], '(unsol ')
        else:
          res1 = 0
        return idx + 1, ((res1 & 1) << 8) | (res & 0xff)
      return idx, 0        

    def decodeampcap(idx, prefix):
      if lines[idx].startswith(prefix):
        res = lines[idx][len(prefix):].strip()
        if res == 'N/A':
          return idx+1, 0
        res, ofs = self.decodeintw(res, 'ofs=')
        res, nsteps = self.decodeintw(res, 'nsteps=')
        res, stepsize = self.decodeintw(res, 'stepsize=')
        res, mute = self.decodeintw(res, 'mute=')
        return idx+1, \
               (ofs & 0x7f) | ((nsteps & 0x7f) << 8) | \
               ((stepsize & 0x7f) << 16) | ((mute & 1) << 31)
      self.wrongfile('amp caps expected')

    def decodegpiocap(idx, prefix):
      if lines[idx].startswith(prefix):
        res = lines[idx][len(prefix):].strip()
        res, io = self.decodeintw(res, 'io=')
        res, o = self.decodeintw(res, 'o=')
        res, i = self.decodeintw(res, 'i=')
        res, unsol = self.decodeintw(res, 'unsolicited=')
        res, wake = self.decodeintw(res, 'wake=')
        return idx+1, \
               (io & 0xff) | ((o & 0xff) << 8) | \
               ((i & 0xff) << 16) | ((unsol & 1) << 30) | ((wake & 1) << 31)
      self.wrongfile('gpio caps expected')

    def decodegpio(idx, prefix):
    
      def writeval(str, idx, var):
        res, val = self.decodeintw(str, var + '=')
        if val:
          self.proc_gpio[var] |= 1 << idx
        else:
          self.proc_gpio[var] &= ~(1 << idx)
        return res
    
      res = lines[idx]
      res, idx1 = self.decodeintw(res, prefix)
      if res.startswith(': '):
        res = res[2:]
      for a in ['enable', 'dir', 'wake', 'sticky', 'data']:
        res = writeval(res, idx1, a)
      if res.find('unsol=') >= 0:
        res = writeval(res, idx1, 'unsol')
      return idx + 1

    self.proc_afg = -1
    self.proc_mfg = -1
    self.proc_nids = {}
    self.proc_afg_function_id = 0
    self.proc_mfg_function_id = 0
    self.proc_vendor_id = 0
    self.proc_subsystem_id = 0
    self.proc_revision_id =0
    function_id = 0
    lines = str.splitlines()
    idx = 0
    idx, self.proc_codec_id = lookfor(idx, 'Codec: ')
    if not self.proc_codec_id:
      print "Proc Text Contents is not valid"
      return
    idx, tmp = lookforint(idx, 'Address: ')
    self.device = tmp # really?
    idx, function_id = decodefcnid(idx, 'Function Id: ')
    idx, self.proc_afg_function_id = decodefcnid(idx, 'AFG Function Id: ')
    idx, self.proc_mfg_function_id = decodefcnid(idx, 'MFG Function Id: ')
    idx, self.proc_vendor_id = lookforint(idx, 'Vendor Id: ')
    idx, self.proc_subsystem_id = lookforint(idx, 'Subsystem Id: ')
    idx, self.proc_revision_id = lookforint(idx, 'Revision Id:' )
    if idx >= len(lines):
      self.wrongfile('id strings expected')
    nomfg = lines[idx].strip() == 'No Modem Function Group found'
    if nomfg:
      self.proc_afg = 1
      if self.proc_afg_function_id == 0:
        self.proc_afg_function_id = function_id
      idx += 1
    elif lines[idx].startswith('Default PCM:'):
      self.proc_afg = 1
      if self.proc_afg_function_id == 0:
        self.proc_afg_function_id = function_id
    else:
      idx, self.proc_mfg = lookforint(idx, 'Modem Function Group: ')
      if not self.proc_mfg is None:
        if self.proc_mfg_function_id == 0:
          self.proc_mfg_function_id = function_id
      else:
        self.proc_mfg = -1
      if idx < len(lines) and lines[idx].startswith('Default PCM:'):
        self.proc_afg = 1
    if self.proc_afg >= 0 and self.proc_afg_function_id == 0:
      self.proc_afg_function_id = 1
    if self.proc_mfg >= 0 and self.proc_mfg_function_id == 0:
      self.proc_mfg_function_id = 2
    if idx >= len(lines):
      return			# probably only modem codec
    if not lines[idx].startswith('Default PCM:'):
      self.wrongfile('default pcm expected')
    if lines[idx+1].strip() == "N/A":
      idx += 2
      self.proc_pcm_bits = 0
      self.proc_pcm_stream = 0
    else:
      idx, tmp1 = decodeint(idx+1, '    rates [')
      idx, tmp2 = decodeint(idx, '    bits [')
      self.proc_pcm_bits = (tmp1 & 0xffff) | ((tmp2 & 0xffff) << 16)
      idx, self.proc_pcm_stream = decodeint(idx, '    formats [')
    idx, self.proc_amp_caps_in = decodeampcap(idx, 'Default Amp-In caps: ')
    idx, self.proc_amp_caps_out = decodeampcap(idx, 'Default Amp-Out caps: ')
    self.proc_gpio = {
      'enable': 0,
      'dir': 0,
      'wake': 0,
      'sticky': 0,
      'data': 0,
      'unsol': 0
    }
    if lines[idx].startswith('State of AFG node'):
      idx += 1
      while lines[idx].startswith('  Power'):
        idx += 1
    self.proc_gpio_cap = 0
    if lines[idx].startswith('GPIO: '):
      idx, self.proc_gpio_cap = decodegpiocap(idx, 'GPIO: ')
      while idx < len(lines) and lines[idx].startswith('  IO['):
        idx = decodegpio(idx, '  IO[')
    if idx >= len(lines):
      return
    line = lines[idx].strip()
    if line == 'Invalid AFG subtree':
      print "Invalid AFG subtree for codec %s?" % self.proc_codec_id
      return
    while line.startswith('Power-Map: ') or \
          line.startswith('Analog Loopback: '):
      print 'Sigmatel specific "%s" verb ignored for the moment' % line
      idx += 1
      line = lines[idx].strip()
    node = None
    while idx < len(lines):
      line = lines[idx]
      idx += 1
      line, nid = self.decodeintw(line, 'Node ')
      pos = line.find('wcaps ')
      if pos < 0:
        self.wrongfile('node wcaps expected')
      line, wcaps = self.decodeintw(line[pos:], 'wcaps ')
      node = ProcNode(self, nid, wcaps)
      if idx >= len(lines):
        break
      line = lines[idx]
      while not line.startswith('Node '):
        if line.startswith('  Device: '):
          node.add_device(line[10:])
        elif line.startswith('  Control: '):
          node.add_control(line[11:])
        elif line.startswith('    ControlAmp: '):
          node.add_controlamp(line[16:])
        elif line.startswith('  Converter: '):
          node.add_converter(line[13:]) 
        elif line.startswith('  SDI-Select: '):
          node.add_sdiselect(line[14:]) 
        elif line.startswith('  Digital:'):
          node.add_digital(line[11:]) 
        elif line.startswith('  Unsolicited:'):
          node.add_unsolicited(line[15:]) 
        elif line.startswith('  Digital category:'):
          node.add_digitalcategory(line[20:]) 
        elif line.startswith('  IEC Coding Type: '):
          pass
        elif line.startswith('  Amp-In caps: '):
          node.add_ampcaps(line[15:], HDA_INPUT) 
        elif line.startswith('  Amp-Out caps: '):
          node.add_ampcaps(line[16:], HDA_OUTPUT) 
        elif line.startswith('  Amp-In vals: '):
          node.add_ampvals(line[15:], HDA_INPUT) 
        elif line.startswith('  Amp-Out vals: '):
          node.add_ampvals(line[17:], HDA_OUTPUT) 
        elif line.startswith('  Connection: '):
          if idx + 1 < len(lines):
            idx += node.add_connection(line[13:], lines[idx+1])
          else:
            idx += node.add_connection(line[13:], '')
        elif line == '  PCM:':
          node.add_pcm(lines[idx+1], lines[idx+2], lines[idx+3])
          idx += 3
        elif line.startswith('  Pincap '):
          node.add_pincap(line[9:])
        elif line.startswith('    Vref caps: '):
          pass
        elif line.startswith('  Pin Default '):
          node.add_pindefault(line[14:])
        elif line.startswith('    Conn = '):
          pass
        elif line.startswith('    DefAssociation = '):
          pass
        elif line.startswith('    Misc = '):
          pass
        elif line.startswith('  Delay: '):
          pass
        elif line.startswith('  Pin-ctls: '):
          node.add_pinctls(line[12:])
        elif line.startswith('  EAPD '):
          node.add_eapd(line[7:])
        elif line.startswith('  Power states: '):
          node.add_powerstates(line[16:])
        elif line.startswith('  Power: '):
          node.add_power(line[9:])
        elif line.startswith('  Processing caps: '):
          node.add_processcaps(line[19:])
        elif line.startswith('  Processing Coefficient: '):
          node.add_processcoef(line[26:])
        elif line.startswith('  Coefficient Index: '):
          node.add_processindex(line[21:])
        elif line.startswith('  Volume-Knob: '):
          node.add_volknob(line[15:])
        elif line.startswith('  In-driver Connection: '):
          idx += 1
          pass
        elif line.startswith('  Devices: '):
          pass
        elif line.startswith('     Dev '):
          pass
        elif line.startswith('    *Dev '):
          pass
        else:
          self.wrongfile(line)
        idx += 1
        if idx < len(lines):
          line = lines[idx]
        else:
          break

  def param_read(self, nid, param):
    if nid == AC_NODE_ROOT:
      if param == PARAMS['VENDOR_ID']:
        return self.proc_vendor_id
      elif param == PARAMS['SUBSYSTEM_ID']:
        return self.proc_subsystem_id
      elif param == PARAMS['REV_ID']:
        return self.proc_revision_id
    elif nid == self.proc_afg:
      if param == PARAMS['FUNCTION_TYPE']:
        return self.proc_afg_function_id
      elif param == PARAMS['PCM']:
        return self.proc_pcm_bits
      elif param == PARAMS['STREAM']:
        return self.proc_pcm_stream
      elif param == PARAMS['AMP_OUT_CAP']:
        return self.proc_amp_caps_out
      elif param == PARAMS['AMP_IN_CAP']:
        return self.proc_amp_caps_in
      elif param == PARAMS['GPIO_CAP']:
        return self.proc_gpio_cap
    elif nid == self.proc_mfg:
      if param == PARAMS['FUNCTION_TYPE']:
        return self.proc_mfg_function_id
    else:
      if nid is None:
        return 0
      node = self.proc_nids[nid]
      return node.param_read(param)
    raise ValueError, "unimplemented param_read(0x%x, 0x%x)" % (nid, param)

  def get_sub_nodes(self, nid):
    if nid == AC_NODE_ROOT:
      if self.proc_mfg >= 0 and self.proc_afg >= 0:
        return 2, self.proc_afg
      if self.proc_mfg >= 0:
        return 1, self.proc_mfg
      return 1, self.proc_afg
    elif nid == self.proc_afg:
      if self.proc_nids:
        return len(self.proc_nids), self.proc_nids.keys()[0]
      return 0, 0
    elif nid is None:
      return 0, 0
    raise ValueError, "unimplemented get_sub_nodes(0x%x)" % nid

  def get_wcap(self, nid):
    node = self.proc_nids[nid]
    return node.wcaps
  
  def get_raw_wcap(self, nid):
    return get_wcap(self, nid)

  def rw(self, nid, verb, param):
    if nid == self.proc_afg:
      for i, j in GPIO_IDS.iteritems():
        if verb == j[0] or verb == j[1]:
          if i == 'direction':
            i = 'dir'
          return self.proc_gpio[i]
      if verb == VERBS['GET_SUBSYSTEM_ID']:
        return self.proc_subsystem_id
    else:
      if nid is None:
        return 0
      node = self.proc_nids[nid]
      return node.rw(verb, param)
    raise ValueError, "unimplemented rw(0x%x, 0x%x, 0x%x)" % (nid, verb, param)

  def dump_node_extra(self, node):
    if not node or not node.nid in self.proc_nids:
      return ''
    node = self.proc_nids[node.nid]
    return node.dump_extra()

  def get_device(self, nid):
    if not nid in self.proc_nids:
      return None
    node = self.proc_nids[nid]
    return node.get_device()

  def get_controls(self, nid):
    if not nid in self.proc_nids:
      return None
    node = self.proc_nids[nid]
    return node.get_controls()

#
# test section
#

def dotest1(base):
  l = listdir(base)
  for f in l:
    file = base + '/' + f
    if os.path.isdir(file):
      dotest1(file)
    else:
      print file
      file = DecodeProcFile(file)
      file = DecodeAlsaInfoFile(file)
      for a in file:
        c = HDACodecProc(0, 0, a)
        c.analyze()

def dotest():
  import sys
  if len(sys.argv) < 2:
    raise ValueError, "Specify directory with codec dumps"
  dotest1(sys.argv[1])

if __name__ == '__main__':
  import os
  from dircache import listdir
  dotest()
