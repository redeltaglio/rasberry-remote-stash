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

import os
import struct
from fcntl import ioctl
from hda_mixer import AlsaMixer, AlsaMixerElem, AlsaMixerElemId

def __ioctl_val(val):
  # workaround for OverFlow bug in python 2.4
  if val & 0x80000000:
    return -((val^0xffffffff)+1)
  return val

IOCTL_INFO = __ioctl_val(0x80dc4801)
IOCTL_PVERSION = __ioctl_val(0x80044810)
IOCTL_VERB_WRITE = __ioctl_val(0xc0084811)
IOCTL_GET_WCAPS = __ioctl_val(0xc0084812)

CTL_IOCTL_CARD_INFO = __ioctl_val(0x81785501)

AC_NODE_ROOT	= 0

(
  HDA_INPUT,
  HDA_OUTPUT
) = range(2)

VERBS = {
  'GET_STREAM_FORMAT':		0x0a00,
  'GET_AMP_GAIN_MUTE':		0x0b00,
  'GET_PROC_COEF':		0x0c00,
  'GET_COEF_INDEX':		0x0d00,
  'PARAMETERS':			0x0f00,
  'GET_CONNECT_SEL':		0x0f01,
  'GET_CONNECT_LIST':		0x0f02,
  'GET_PROC_STATE':		0x0f03,
  'GET_SDI_SELECT':		0x0f04,
  'GET_POWER_STATE':		0x0f05,
  'GET_CONV':			0x0f06,
  'GET_PIN_WIDGET_CONTROL':	0x0f07,
  'GET_UNSOLICITED_RESPONSE':	0x0f08,
  'GET_PIN_SENSE':		0x0f09,
  'GET_BEEP_CONTROL':		0x0f0a,
  'GET_EAPD_BTLENABLE':		0x0f0c,
  'GET_DIGI_CONVERT_1':		0x0f0d,
  'GET_DIGI_CONVERT_2':		0x0f0e,
  'GET_VOLUME_KNOB_CONTROL':	0x0f0f,
  'GET_GPIO_DATA':		0x0f15,
  'GET_GPIO_MASK':		0x0f16,
  'GET_GPIO_DIRECTION':		0x0f17,
  'GET_GPIO_WAKE_MASK':		0x0f18,
  'GET_GPIO_UNSOLICITED_RSP_MASK': 0x0f19,
  'GET_GPIO_STICKY_MASK':	0x0f1a,
  'GET_CONFIG_DEFAULT':		0x0f1c,
  'GET_SUBSYSTEM_ID':		0x0f20,

  'SET_STREAM_FORMAT':		0x200,
  'SET_AMP_GAIN_MUTE':		0x300,
  'SET_PROC_COEF':		0x400,
  'SET_COEF_INDEX':		0x500,
  'SET_CONNECT_SEL':		0x701,
  'SET_PROC_STATE':		0x703,
  'SET_SDI_SELECT':		0x704,
  'SET_POWER_STATE':		0x705,
  'SET_CHANNEL_STREAMID':	0x706,
  'SET_PIN_WIDGET_CONTROL':	0x707,
  'SET_UNSOLICITED_ENABLE':	0x708,
  'SET_PIN_SENSE':		0x709,
  'SET_BEEP_CONTROL':		0x70a,
  'SET_EAPD_BTLENABLE':		0x70c,
  'SET_DIGI_CONVERT_1':		0x70d,
  'SET_DIGI_CONVERT_2':		0x70e,
  'SET_VOLUME_KNOB_CONTROL':	0x70f,
  'SET_GPIO_DATA':		0x715,
  'SET_GPIO_MASK':		0x716,
  'SET_GPIO_DIRECTION':		0x717,
  'SET_GPIO_WAKE_MASK':		0x718,
  'SET_GPIO_UNSOLICITED_RSP_MASK': 0x719,
  'SET_GPIO_STICKY_MASK':	0x71a,
  'SET_CONFIG_DEFAULT_BYTES_0':	0x71c,
  'SET_CONFIG_DEFAULT_BYTES_1':	0x71d,
  'SET_CONFIG_DEFAULT_BYTES_2':	0x71e,
  'SET_CONFIG_DEFAULT_BYTES_3':	0x71f,
  'SET_CODEC_RESET':		0x7ff
}

PARAMS = {
  'VENDOR_ID':		0x00,
  'SUBSYSTEM_ID':	0x01,
  'REV_ID':		0x02,
  'NODE_COUNT':		0x04,
  'FUNCTION_TYPE':	0x05,
  'AUDIO_FG_CAP':	0x08,
  'AUDIO_WIDGET_CAP':	0x09,
  'PCM':		0x0a,
  'STREAM':		0x0b,
  'PIN_CAP':		0x0c,
  'AMP_IN_CAP':		0x0d,
  'CONNLIST_LEN':	0x0e,
  'POWER_STATE':	0x0f,
  'PROC_CAP':		0x10,
  'GPIO_CAP':		0x11,
  'AMP_OUT_CAP':	0x12,
  'VOL_KNB_CAP':	0x13
}

WIDGET_TYPES = {
  'AUD_OUT':		0x00,
  'AUD_IN':		0x01,
  'AUD_MIX':		0x02,
  'AUD_SEL':		0x03,
  'PIN':		0x04,
  'POWER':		0x05,
  'VOL_KNB':		0x06,
  'BEEP':		0x07,
  'VENDOR':		0x0f
}

WIDGET_TYPE_NAMES = [
  "Audio Output",
  "Audio Input",
  "Audio Mixer",
  "Audio Selector",
  "Pin Complex",
  "Power Widget",
  "Volume Knob Widget",
  "Beep Generator Widget",
  None,
  None,
  None,
  None,
  None,
  None,
  None,
  "Vendor Defined Widget"
]

WIDGET_TYPE_IDS = [
  "AUD_OUT",
  "AUD_IN",
  "AUD_MIX",
  "AUD_SEL",
  "PIN",
  "POWER",
  "VOL_KNB",
  "BEEP",
  None,
  None,
  None,
  None,
  None,
  None,
  None,
  "VENDOR"
]

WIDGET_CAP_NAMES = {
  'STEREO': 'Stereo',
  'IN_AMP': 'Input Amplifier',
  'OUT_AMP': 'Output Amplifier',
  'AMP_OVRD': 'Amplifier Override',
  'FORMAT_OVRD': 'Format Override',
  'STRIPE': 'Stripe',
  'PROC_WID': 'Proc Widget',
  'CONN_LIST': 'Connection List',
  'UNSOL_CAP': 'Unsolicited Capabilities',
  'DIGITAL': 'Digital',
  'POWER': 'Power',
  'LR_SWAP': 'L/R Swap',
  'CP_CAPS': 'CP Capabilities'
}

WIDGET_PINCAP_NAMES = {
  'IMP_SENSE': 'Input Sense',
  'TRIG_REQ': 'Trigger Request',
  'PRES_DETECT': 'Press Detect',
  'HP_DRV': 'Headphone Drive',
  'OUT': 'Output',
  'IN': 'Input',
  'BALANCE': 'Balance',
  'HDMI': 'HDMI',
  'EAPD': 'EAPD',
  'DP': 'Display Port',
  'HBR': 'Hight Bit Rate',
}

GPIO_IDS = {
  'enable': (VERBS['GET_GPIO_MASK'], VERBS['SET_GPIO_MASK']),
  'direction': (VERBS['GET_GPIO_DIRECTION'], VERBS['SET_GPIO_DIRECTION']),
  'wake': (VERBS['GET_GPIO_WAKE_MASK'], VERBS['SET_GPIO_WAKE_MASK']),
  'unsol': (VERBS['GET_GPIO_UNSOLICITED_RSP_MASK'], VERBS['SET_GPIO_UNSOLICITED_RSP_MASK']),
  'sticky': (VERBS['GET_GPIO_STICKY_MASK'], VERBS['SET_GPIO_STICKY_MASK']),
  'data': (VERBS['GET_GPIO_DATA'], VERBS['SET_GPIO_DATA'])
}

EAPDBTL_BITS = {
  'BALANCED': 0,
  'EAPD': 1,
  'R/L': 2
} 

PIN_WIDGET_CONTROL_BITS = {
  'IN': 5,
  'OUT': 6,
  'HP': 7
}

PIN_WIDGET_CONTROL_VREF = [
  "HIZ", "50", "GRD", None, "80", "100", None, None
]

DIG1_BITS = {
  'ENABLE': 0,
  'VALIDITY': 1,
  'VALIDITYCFG': 2,
  'EMPHASIS': 3,
  'COPYRIGHT': 4,
  'NONAUDIO': 5,
  'PROFESSIONAL': 6,
  'LEVEL': 7
}

POWER_STATES = ["D0", "D1", "D2", "D3", "D3cold", "S3D3cold", "CLKSTOP", "EPSS"]

class HDAAmpCaps:

  def __init__(self, codec, nid, dir):
    self.codec = codec
    self.nid = nid
    self.dir = dir
    self.cloned = False
    self.reread()
    
  def reread(self):
    caps = self.codec.param_read(self.nid,
          PARAMS[self.dir == HDA_OUTPUT and 'AMP_OUT_CAP' or 'AMP_IN_CAP'])
    if caps == ~0 or caps == 0:
      if self.dir == HDA_INPUT:
        ccaps = self.codec.amp_caps_in
      else:
        ccaps = self.codec.amp_caps_out
      if ccaps:
        ccaps.clone(self)
      else:
        self.ofs = self.nsteps = self.stepsize = self.mute = None
    else:
      self.ofs = caps & 0x7f
      self.nsteps = (caps >> 8) & 0x7f
      self.stepsize = (caps >> 16) & 0x7f
      self.mute = (caps >> 31) & 1 and True or False

  def clone(self, ampcaps):
    ampcaps.ofs = self.ofs
    ampcaps.nsteps = self.nsteps
    ampcaps.stepsize = self.stepsize
    ampcaps.mute = self.mute
    ampcaps.cloned = True

  def get_val_db(self, val):
    if self.ofs is None:
      return None
    if val & 0x80:
      return -999999
    range = (self.stepsize + 1) * 25
    off = -self.ofs * range
    if val > self.nsteps:
      db = off + self.nsteps * range
      if val != 0 or self.nsteps != 0:
        print "val > nsteps? for nid 0x%02x" % self.nid, val, self.nsteps
    else:
      db = off + val * range
    return db

  def get_val_perc(self, val):
    if self.ofs is None:
      return None
    if self.nsteps == 0:
      return 0
    return (val * 100) / self.nsteps

  def get_val_str(self, val):
    if self.ofs is None:
      return "0x%02x" % val
    else:
      db = self.get_val_db(val & 0x7f)
      res = val & 0x80 and "{mute-" or "{"
      res += "0x%02x" % (val & 0x7f)
      res += ":%02i.%idB" % (db / 100, db % 100)
      res += ":%i%%}" % (self.get_val_perc(val & 0x7f))
      return res

class HDAAmpVal:

  def __init__(self, codec, node, dir, caps):
    self.codec = codec
    self.node = node
    self.dir = dir
    if caps.ofs == None:
      self.caps = dir == HDA_INPUT and codec.amp_caps_in or codec.amp_caps_out
    else:
      self.caps = caps
    self.nid = node.nid
    self.stereo = node.stereo
    self.indices = 1
    self.origin_vals = None
    if dir == HDA_INPUT:
      if node.wtype_id == 'PIN':
        self.indices = 1
      elif node.connections:
        self.indices = len(node.connections)
      else:
        self.indices = 0
    self.reread()

  def __write_val(self, idx):
    dir = self.dir == HDA_OUTPUT and (1<<15) or (1<<14)
    verb = VERBS['SET_AMP_GAIN_MUTE']
    if self.stereo:
      indice = idx / 2
      dir |= idx & 1 and (1 << 12) or (1 << 13)
    else:
      indice = idx
      dir |= (1 << 12) | (1 << 13)
    self.codec.rw(self.nid, verb, dir | (indice << 8) | self.vals[idx])

  def set_mute(self, idx, mute):
    val = self.vals[idx]
    if mute:
      changed = (self.vals[idx] & 0x80) == 0
      self.vals[idx] |= 0x80
    else:
      changed = (self.vals[idx] & 0x80) == 0x80
      self.vals[idx] &= ~0x80
    self.__write_val(idx)
    return changed
    
  def set_value(self, idx, val):
    changed = (self.vals[idx] & 0x7f) != val
    self.vals[idx] &= ~0x7f
    self.vals[idx] |= val & 0x7f
    self.__write_val(idx)
    return changed
    
  def reread(self):
    dir = self.dir == HDA_OUTPUT and (1<<15) or (0<<15)
    self.vals = []
    verb = VERBS['GET_AMP_GAIN_MUTE']
    for i in range(self.indices):
      if self.stereo:
        val = self.codec.rw(self.nid, verb, (1 << 13) | dir | i)
        self.vals.append(val)
      val = self.codec.rw(self.nid, verb, (0 << 13) | dir | i)
      self.vals.append(val)
    if self.origin_vals == None:
      self.origin_vals = self.vals[:]

  def revert(self):
    self.vals = self.origin_vals[:]
    for idx in range(len(self.vals)):
      self.__write_val(idx)

  def export(self):
    vals = self.vals[:]
    self.codec.export_start(True)
    self.revert()
    self.codec.export_end()
    self.vals = vals
    for idx in range(len(self.vals)):
      self.__write_val(idx)    

  def get_val(self, idx):
    if self.stereo:
      return [self.vals[idx*2], self.vals[idx*2+1]]
    return self.vals[idx]

  def get_val_db(self, idx):
    vals = self.get_val(idx)
    if type(vals) != type([]):
      vals = [vals]
    res = []
    for val in vals:
      res.append(self.caps.get_val_db(val))
    return res

  def get_val_str(self, idx):

    def niceval(val):
      return self.caps.get_val_str(val)

    if self.stereo:
      return '[' + niceval(self.vals[idx*2]) + ' ' + niceval(self.vals[idx*2+1]) + ']'
    return niceval(self.vals[idx])

class HDARootNode:

  def __init__(self, codec, _name):
    self.codec = codec
    self._name = _name

  def name(self):
    return self._name

class HDANode:
  
  def __init__(self, codec, nid, cache=True):
    self.codec = codec
    self.nid = nid
    self.wcaps = cache and codec.get_wcap(nid) or codec.get_raw_wcap(nid)
    self.stereo = (self.wcaps & (1 << 0)) and True or False
    self.in_amp = (self.wcaps & (1 << 1)) and True or False
    self.out_amp = (self.wcaps & (1 << 2)) and True or False
    self.amp_ovrd = (self.wcaps & (1 << 3)) and True or False
    self.format_ovrd = (self.wcaps & (1 << 4)) and True or False
    self.stripe = (self.wcaps & (1 << 5)) and True or False
    self.proc_wid = (self.wcaps & (1 << 6)) and True or False
    self.unsol_cap = (self.wcaps & (1 << 7)) and True or False
    self.conn_list = (self.wcaps & (1 << 8)) and True or False
    self.digital = (self.wcaps & (1 << 9)) and True or False
    self.power = (self.wcaps & (1 << 10)) and True or False
    self.lr_swap = (self.wcaps & (1 << 11)) and True or False
    self.cp_caps = (self.wcaps & (1 << 12)) and True or False
    self.chan_cnt_ext = (self.wcaps >> 13) & 7
    self.wdelay = (self.wcaps >> 16) & 0x0f
    self.wtype = (self.wcaps >> 20) & 0x0f
    self.channels = ((self.chan_cnt_ext << 1) | 1) + 1
    self.wtype_id = WIDGET_TYPE_IDS[self.wtype]
    if self.wtype_id == 'VOL_KNB': self.conn_list = True

    self.wcaps_list = []
    if self.stereo: self.wcaps_list.append('STEREO')
    if self.in_amp: self.wcaps_list.append('IN_AMP')
    if self.out_amp: self.wcaps_list.append('OUT_AMP')
    if self.amp_ovrd: self.wcaps_list.append('AMP_OVRD')
    if self.format_ovrd: self.wcaps_list.append('FORMAT_OVRD')
    if self.stripe: self.wcaps_list.append('STRIPE')
    if self.proc_wid: self.wcaps_list.append('PROC_WID')
    if self.unsol_cap: self.wcaps_list.append('UNSOL_CAP')
    if self.conn_list: self.wcaps_list.append('CONN_LIST')
    if self.digital: self.wcaps_list.append('DIGITAL')
    if self.power: self.wcaps_list.append('POWER')
    if self.lr_swap: self.wcaps_list.append('LR_SWAP')
    if self.cp_caps: self.wcaps_list.append('CP_CAPS')

    self.origin_active_connection = None
    self.origin_pwr = None
    self.origin_digi1 = None
    self.origin_pincap_eapdbtls = None
    self.origin_pinctls = None
    self.origin_vol_knb = None
    self.origin_sdi_select = None

    self.disable_reread = False

    self.reread()
    
  def wtype_name(self):
    name = WIDGET_TYPE_NAMES[self.wtype]
    if not name:
      return "UNKNOWN Widget 0x%x" % self.wtype
    return name
    
  def wcap_name(self, id):
    return WIDGET_CAP_NAMES[id]

  def pincap_name(self, id):
    return WIDGET_PINCAP_NAMES[id]

  def name(self):
    return self.wtype_name() + " [0x%02x]" % self.nid

  def set_active_connection(self, val):
    changed = False
    if self.active_connection != None:
      changed = self.active_connection != val 
      self.codec.rw(self.nid, VERBS['SET_CONNECT_SEL'], val)
      if not self.disable_reread:
        self.active_connection = self.codec.rw(self.nid, VERBS['GET_CONNECT_SEL'], 0)
      else:
        self.active_connection = val
    return changed

  def reread_pwr(self, value=None):
      if value is None:
        pwr = self.codec.rw(self.nid, VERBS['GET_POWER_STATE'], 0)
      else:
        pwr = value
      self.pwr = pwr
      if self.origin_pwr is None:
        self.origin_pwr = pwr
      self.pwr_setting = pwr & 0x0f
      self.pwr_actual = (pwr >> 4) & 0x0f
      self.pwr_setting_name = self.pwr_setting < 4 and POWER_STATES[self.pwr_setting] or "UNKNOWN"
      self.pwr_actual_name = self.pwr_actual < 4 and POWER_STATES[self.pwr_actual] or "UNKNOWN"
    
  def reread(self):
  
    def get_jack_location(cfg):
      bases = ["N/A", "Rear", "Front", "Left", "Right", "Top", "Bottom"]
      specials = {0x07: "Rear Panel", 0x08: "Drive Bar",
                  0x17: "Riser", 0x18: "HDMI", 0x19: "ATAPI",
                  0x37: "Mobile-In", 0x38: "Mobile-Out"}
      cfg = (cfg >> 24) & 0x3f
      if cfg & 0x0f < 7:
        return bases[cfg & 0x0f]
      if cfg in specials:
        return specials[cfg]
      return "UNKNOWN"
      
    def get_jack_connector(cfg):
      names = ["Unknown", "1/8", "1/4", "ATAPI", "RCA", "Optical",
               "Digital", "Analog", "DIN", "XLR", "RJ11", "Comb",
               None, None, None, "Other"]
      cfg = (cfg >> 16) & 0x0f
      return names[cfg] and names[cfg] or "UNKNOWN"
      
    def get_jack_color(cfg):
      names = ["Unknown", "Black", "Grey", "Blue", "Green", "Red", "Orange",
               "Yellow", "Purple", "Pink", None, None, None, None, "White",
               "Other"]
      cfg = (cfg >> 12) & 0x0f
      return names[cfg] and names[cfg] or "UNKNOWN"
  
    self.connections = None
    self.active_connection = None
    if self.conn_list:
      self.connections = self.codec.get_connections(self.nid)
      if not self.wtype_id in ['AUD_MIX', 'VOL_KNB', 'POWER']:
        self.active_connection = self.codec.rw(self.nid, VERBS['GET_CONNECT_SEL'], 0)
        if self.origin_active_connection == None:
          self.origin_active_connection = self.active_connection
    if self.in_amp:
      self.amp_caps_in = HDAAmpCaps(self.codec, self.nid, HDA_INPUT)
      self.amp_vals_in = HDAAmpVal(self.codec, self, HDA_INPUT, self.amp_caps_in)
    if self.out_amp:
      self.amp_caps_out = HDAAmpCaps(self.codec, self.nid, HDA_OUTPUT)
      self.amp_vals_out = HDAAmpVal(self.codec, self, HDA_OUTPUT, self.amp_caps_out)
    if self.wtype_id == 'PIN':
      jack_conns = ["Jack", "N/A", "Fixed", "Both"]
      jack_types = ["Line Out", "Speaker", "HP Out", "CD", "SPDIF Out",
                    "Digital Out", "Modem Line", "Modem Hand",
                    "Line In", "Aux", "Mic", "Telephony", "SPDIF In",
                    "Digital In", "Reserved", "Other"]
      jack_locations = ["Ext", "Int", "Sep", "Oth"]

      caps = self.codec.param_read(self.nid, PARAMS['PIN_CAP'])
      self.pincaps = caps
      self.pincap = []
      if caps & (1 << 0): self.pincap.append('IMP_SENSE')
      if caps & (1 << 1): self.pincap.append('TRIG_REQ')
      if caps & (1 << 2): self.pincap.append('PRES_DETECT')
      if caps & (1 << 3): self.pincap.append('HP_DRV')
      if caps & (1 << 4): self.pincap.append('OUT')
      if caps & (1 << 5): self.pincap.append('IN')
      if caps & (1 << 6): self.pincap.append('BALANCE')
      if caps & (1 << 7): self.pincap.append('HDMI')
      if caps & (1 << 16): self.pincap.append('EAPD')
      if caps & (1 << 24): self.pincap.append('DP')	# display port
      if caps & (1 << 27): self.pincap.append('HBR')
      self.pincap_vref = []
      if caps & (1 << 8): self.pincap_vref.append('HIZ')
      if caps & (1 << 9): self.pincap_vref.append('50')
      if caps & (1 << 10): self.pincap_vref.append('GRD')
      if caps & (1 << 12): self.pincap_vref.append('80')
      if caps & (1 << 13): self.pincap_vref.append('100')
      self.reread_eapdbtl()
      caps = self.codec.rw(self.nid, VERBS['GET_CONFIG_DEFAULT'], 0)
      self.defcfg_pincaps = caps
      self.jack_conn_name = jack_conns[(caps >> 30) & 0x03]
      self.jack_type_name = jack_types[(caps >> 20) & 0x0f]
      self.jack_location_name = jack_locations[(caps >> 28) & 0x03]
      self.jack_location2_name = get_jack_location(caps)
      self.jack_connector_name = get_jack_connector(caps)
      self.jack_color_name = get_jack_color(caps)
      self.defcfg_assoc = (caps >> 4) & 0x0f
      self.defcfg_sequence = (caps >> 0) & 0x0f
      self.defcfg_misc = []
      if caps & (1 << 8): self.defcfg_misc.append('NO_PRESENCE')
      self.reread_pin_widget_control()
    elif self.wtype_id == 'VOL_KNB':
      cap = self.codec.param_read(self.nid, PARAMS['VOL_KNB_CAP'])
      self.vol_knb_delta = (cap >> 7) & 1
      self.vol_knb_steps = cap & 0x7f
      self.reread_vol_knb()
    elif self.wtype_id in ['AUD_IN', 'AUD_OUT']:
      conv = self.codec.rw(self.nid, VERBS['GET_CONV'], 0)
      self.aud_stream = (conv >> 4) & 0x0f
      self.aud_channel = (conv >> 0) & 0x0f
      self.reread_sdi_select()
      self.reread_dig1()
      if self.format_ovrd:
        pcm = self.codec.param_read(self.nid, PARAMS['PCM'])
        stream = self.codec.param_read(self.nid, PARAMS['STREAM'])
        self.pcm_rate = pcm & 0xffff
        self.pcm_rates = self.codec.analyze_pcm_rates(self.pcm_rate)
        self.pcm_bit = pcm >> 16
        self.pcm_bits = self.codec.analyze_pcm_bits(self.pcm_bit)
        self.pcm_stream = stream
        self.pcm_streams = self.codec.analyze_pcm_streams(self.pcm_stream)
    if self.proc_wid:
      proc_caps = self.codec.param_read(self.nid, PARAMS['PROC_CAP'])
      self.proc_benign = proc_caps & 1 and True or False
      self.proc_numcoef = (proc_caps >> 8) & 0xff
    if self.unsol_cap:
      unsol = self.codec.rw(self.nid, VERBS['GET_UNSOLICITED_RESPONSE'], 0)
      self.unsol_tag = unsol & 0x3f
      self.unsol_enabled = (unsol & (1 << 7)) and True or False
    if self.power:
      pwr = self.codec.param_read(self.nid, PARAMS['POWER_STATE'])
      self.pwr_state = pwr
      self.pwr_states = []
      for a in range(len(POWER_STATES)):
        if pwr & (1 << a):
          self.pwr_states.append(POWER_STATES[a])
      self.reread_pwr()
    # NID 0x20 == Realtek Define Registers
    if self.codec.vendor_id == 0x10ec and self.nid == 0x20:
      self.realtek_coeff_proc = self.codec.rw(self.nid, VERBS['GET_PROC_COEF'], 0)
      self.realtek_coeff_index = self.codec.rw(self.nid, VERBS['GET_COEF_INDEX'], 0)

  def reread_eapdbtl(self, value=None):
    self.pincap_eapdbtl = []
    self.pincap_eapdbtls = 0
    if not 'EAPD' in self.pincap:
      return
    if value is None:
      val = self.codec.rw(self.nid, VERBS['GET_EAPD_BTLENABLE'], 0)
    else:
      val = value
    self.pincap_eapdbtls = val
    if self.origin_pincap_eapdbtls is None:
      self.origin_pincap_eapdbtls = val
    for name in EAPDBTL_BITS:
      bit = EAPDBTL_BITS[name]
      if val & (1 << bit): self.pincap_eapdbtl.append(name)

  def eapdbtl_set_value(self, name, value):
    mask = 1 << EAPDBTL_BITS[name]
    value = value and True or False
    changed = (self.pincap_eapdbtls & mask) and not value or value
    if value:
      self.pincap_eapdbtls |= mask
    else:
      self.pincap_eapdbtls &= ~mask
    self.codec.rw(self.nid, VERBS['SET_EAPD_BTLENABLE'], self.pincap_eapdbtls)
    self.reread_eapdbtl()
    return changed

  def reread_pin_widget_control(self, value=None):
    if value is None:
      pinctls = self.codec.rw(self.nid, VERBS['GET_PIN_WIDGET_CONTROL'], 0)
    else:
      pinctls = value
    self.pinctls = pinctls
    if self.origin_pinctls is None:
      self.origin_pinctls = pinctls
    self.pinctl = []
    for name in PIN_WIDGET_CONTROL_BITS:
      bit = PIN_WIDGET_CONTROL_BITS[name]
      if pinctls & (1 << bit): self.pinctl.append(name)
    self.pinctl_vref = None
    if self.pincap_vref:
      self.pinctl_vref = PIN_WIDGET_CONTROL_VREF[pinctls & 0x07]

  def pin_widget_control_set_value(self, name, value):
    if name in PIN_WIDGET_CONTROL_BITS:
      mask = 1 << PIN_WIDGET_CONTROL_BITS[name]
      value = value and True or False
      changed = (self.pinctls & mask) and not value or value
      if value:
        self.pinctls |= mask
      else:
        self.pinctls &= ~mask
    elif name == 'vref' and self.pincap_vref:
      idx = PIN_WIDGET_CONTROL_VREF.index(value)
      changed = (self.pinctls & 0x07) != idx
      self.pinctls &= ~0x07
      self.pinctls |= idx
    self.codec.rw(self.nid, VERBS['SET_PIN_WIDGET_CONTROL'], self.pinctls)
    self.reread_pin_widget_control()
    return changed

  def reread_vol_knb(self, value=None):
    if value is None:
      cap = self.codec.rw(self.nid, VERBS['GET_VOLUME_KNOB_CONTROL'], 0)
    else:
      cap = value
    self.vol_knb = cap
    if self.origin_vol_knb is None:
      self.origin_vol_knb = cap
    self.vol_knb_direct = (cap >> 7) & 1
    self.vol_knb_val = cap & 0x7f
    
  def vol_knb_set_value(self, name, value):
    if name == 'direct':
      value = value and True or False
      changed = (self.vol_knb & (1 << 7)) and not value or value      
      if value:
        self.vol_knb |= (1 << 7)
      else:
        self.vol_knb &= ~(1 << 7)
    elif name == 'value':
      changed = (self.vol_knb & 0x7f) != value
      self.vol_knb &= ~0x7f
      self.vol_knb |= value
    self.codec.rw(self.nid, VERBS['SET_VOLUME_KNOB_CONTROL'], self.vol_knb)
    self.reread_vol_knb()
    return changed

  def reread_sdi_select(self, value=None):
    self.sdi_select = None
    if self.wtype_id == 'AUD_IN' and self.aud_channel == 0:
      if value is None:
        sdi = self.codec.rw(self.nid, VERBS['GET_SDI_SELECT'], 0)
      else:
        sdi = value
      self.sdi_select = sdi & 0x0f
      if self.origin_sdi_select is None:
        self.origin_sdi_select = sdi

  def sdi_select_set_value(self, value):
    changed = False
    if self.sdi_select != None:
      changed = (self.sdi_select & 0x0f) != value
      self.sdi_select = value & 0x0f
      self.codec.rw(self.nid, VERBS['SET_SDI_SELECT'], self.sdi_select)
      self.reread_sdi_select()
    return changed

  def reread_dig1(self, value=None):
    self.dig1 = []
    self.dig1_category = None
    if not self.digital:
      return
    if value is None:
      digi1 = self.codec.rw(self.nid, VERBS['GET_DIGI_CONVERT_1'], 0)
    else:
      digi1 = value
    self.digi1 = digi1
    if self.origin_digi1 is None:
      self.origin_digi1 = digi1
    for name in DIG1_BITS:
      bit = DIG1_BITS[name]
      if digi1 & (1 << bit): self.dig1.append(name)
    self.dig1_category = (digi1 >> 8) & 0x7f

  def dig1_set_value(self, name, value):
    if name == 'category':
      changed = ((self.digi1 >> 8) & 0x7f) != (value & 0x7f)
      self.digi1 &= ~0x7f00
      self.digi1 |= (value & 0x7f) << 8
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_2'], (self.digi1 >> 8) & 0xff)
    else:
      mask = 1 << DIG1_BITS[name]
      value = value and True or False
      changed = (self.digi1 & mask) and not value or value      
      if value:
        self.digi1 |= mask
      else:
        self.digi1 &= ~mask
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_1'], self.digi1 & 0xff)
    self.reread_dig1()
    return changed

  def revert(self, export=False):
    if not self.origin_active_connection is None:
      self.set_active_connection(self.origin_active_connection)
    if not self.origin_pwr is None:
      self.codec.rw(self.nid, VERBS['SET_POWER_STATE'], self.origin_pwr)
      self.reread_pwr(self.origin_pwr)
    if not self.origin_pinctls is None:
      self.codec.rw(self.nid, VERBS['SET_PIN_WIDGET_CONTROL'], self.origin_pinctls)
      self.reread_pin_widget_control(self.origin_pinctls)
    if not export:
      if self.in_amp:
        self.amp_vals_in.revert()
      if self.out_amp:
        self.amp_vals_out.revert()
    if not self.origin_pincap_eapdbtls is None:
      self.codec.rw(self.nid, VERBS['SET_EAPD_BTLENABLE'], self.origin_pincap_eapdbtls)
      self.reread_eapdbtl(self.origin_pincap_eapdbtls)
    if not self.origin_vol_knb is None:
      self.codec.rw(self.nid, VERBS['SET_VOLUME_KNOB_CONTROL'], self.origin_vol_knb)
      self.set_vol_knb(self.origin_vol_knb)
    if not self.origin_sdi_select is None:
      self.codec.rw(self.nid, VERBS['SET_SDI_SELECT'], self.origin_sdi_select)
      self.reread_sdi_select(self.origin_sdi_select)
    if not self.origin_digi1 is None:
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_1'], self.origin_digi1 & 0xff)
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_2'], (self.origin_digi1 >> 8) & 0xff)
      self.reread_dig1(self.origin_digi1)

  def export(self):
    
    def getit(cur, orig):
      if orig is None:
        return None
      return getattr(self, cur)
  
    self.disable_reread = True
    active_connection = getit('active_connection', self.origin_active_connection)
    pwr = getit('pwr', self.origin_pwr)
    pinctls = getit('pinctls', self.origin_pinctls)
    pincap_eapdbtls = getit('pincap_eapdbtls', self.origin_pincap_eapdbtls)
    vol_knb = getit('vol_knb', self.origin_vol_knb)
    sdi_select = getit('sdi_select', self.origin_sdi_select)
    digi1 = getit('digi1', self.origin_digi1)
    self.codec.export_start(True)
    self.revert(export=True)
    self.codec.export_end()
    if not self.origin_active_connection is None:
      self.set_active_connection(active_connection)
    if not self.origin_pwr is None:
      self.codec.rw(self.nid, VERBS['SET_POWER_STATE'], pwr)
      self.reread_pwr(pwr)
    if not self.origin_pinctls is None:
      self.codec.rw(self.nid, VERBS['SET_PIN_WIDGET_CONTROL'], pinctls)
      self.reread_pin_widget_control(pinctls)
    if self.in_amp:
      self.amp_vals_in.export()
    if self.out_amp:
      self.amp_vals_out.export()
    if not self.origin_pincap_eapdbtls is None:
      self.codec.rw(self.nid, VERBS['SET_EAPD_BTLENABLE'], pincap_eapdbtls)
      self.reread_eapdbtl(pincap_eapdbtls)
    if not self.origin_vol_knb is None:
      self.codec.rw(self.nid, VERBS['SET_VOLUME_KNOB_CONTROL'], vol_knb)
      self.set_vol_knb(vol_knb)
    if not self.origin_sdi_select is None:
      self.codec.rw(self.nid, VERBS['SET_SDI_SELECT'], sdi_select)
      self.reread_sdi_select(sdi_select)
    if not self.origin_digi1 is None:
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_1'], digi1 & 0xff)
      self.codec.rw(self.nid, VERBS['SET_DIGI_CONVERT_2'], (digi1 >> 8) & 0xff)
      self.reread_dig1(digi1)    
    self.disable_reread = False

  def get_device(self):
    return self.codec.get_device(self.nid)

  def get_controls(self):
    return self.codec.get_controls(self.nid)

  def get_mixercontrols(self):
    if not self.codec.mixer:
      return []
    ctls = self.get_controls()
    res = []
    for ctl in ctls:
      for iface in (ctl.iface and [ctl.iface] or [None, 'card', 'pcm']):
        try:
          id = AlsaMixerElemId(iface=iface, name=ctl.name, index=ctl.index, device=ctl.device)
          e = AlsaMixerElem(self.codec.mixer, id)
          if iface and ctl.iface != iface:
            ctl.iface = iface
          break
        except:
          e = None
      if not e:
        print "Control ID not found:", ctl.dump_extra().strip().lstrip()
        continue
      e.hdactl = ctl
      res.append(e)
    return res

  def get_conn_amp_vals_str(self, dst_node):
    # return amp values for connection between this and dst_node
    res = []
    if self.out_amp:
      res.append(self.amp_vals_out.get_val_str(0))
    else:
      res.append(None)
    if dst_node.in_amp:
      idx = 0
      if dst_node.amp_vals_in.indices == dst_node.connections:
        if not self.nid in dst_node.connections:
          raise ValueError, "nid 0x%02x is not connected to nid 0x%02x (%s, %s)" % (dst_node.nid, self.nid, repr(self.connections), repr(dst_node.connections))
        idx = dst_node.connections.index(self.nid)
      res.append(dst_node.amp_vals_in.get_val_str(idx))
    else:
      res.append(None)
    return res

  def is_conn_active(self, dst_node):
    # disabled route for PIN widgets
    if self.wtype_id == 'PIN' and not 'IN' in self.pinctl:
      return None
    if dst_node.wtype_id == 'PIN' and not 'OUT' in dst_node.pinctl:
      return None
    res = [None, None]
    if self.out_amp:
      vals = self.amp_vals_out.get_val_db(0)
      for idx in range(len(vals)):
        if res[idx]:
          res[idx] += vals[idx]
        else:
          res[idx] = vals[idx]
    if dst_node.in_amp:
      idx = 0
      if dst_node.amp_vals_in.indices == dst_node.connections:
        if not self.nid in dst_node.connections:
          raise ValueError, "nid 0x%02x is not connected to nid 0x%02x (%s, %s)" % (dst_node.nid, self.nid, repr(self.connections), repr(dst_node.connections))
        idx = dst_node.connections.index(self.nid)
      vals = dst_node.amp_vals_in.get_val_db(idx)
      for idx in range(len(vals)):
        if res[idx]:
          res[idx] += vals[idx]
        else:
          res[idx] = vals[idx]
    if res[0] is None and res[1] is None:
      return True
    limit = self.wtype_id == 'AUD_OUT' and -3200 or -1200
    for r in res:
      if r >= limit:
        return True
    return False

class HDAGPIO:

  def __init__(self, codec, nid):
    self.codec = codec
    self.nid = nid
    self.originval = None
    self.disable_reread = False
    self.reread()

  def reread(self):
    self.val = {}
    for i in GPIO_IDS:
     self.val[i] = self.codec.rw(self.nid, GPIO_IDS[i][0], 0)
    if self.originval == None:
      self.originval = self.val.copy()

  def test(self, name, bit):
    return (self.val[name] & (1 << bit)) and True or False

  def read(self, name):
    self.val[name] = self.codec.rw(self.nid, GPIO_IDS[name][0], 0)

  def write(self, name):
    self.codec.rw(self.nid, GPIO_IDS[name][1], self.val[name])
    if not self.disable_reread:
      self.read(name)

  def set(self, name, bit, val):
    old = self.test(name, bit)
    if val:
      self.val[name] |= 1 << bit
    else:
      self.val[name] &= ~(1 << bit)
    if old == self.test(name, bit):
      return False
    self.write(name)
    return True

  def revert(self):
    for i in GPIO_IDS:
      self.val[i] = self.originval[i]
      self.write(i)

  def export(self):
    self.disable_reread = True
    vals = self.val.copy()
    self.codec.export_start(True)
    self.revert()
    self.codec.export_end()
    self.val = vals
    for i in GPIO_IDS:
      self.write(i)
    self.disable_reread = False
  
class HDACard:

  def __init__(self, card, ctl_fd=None):
    self.card = card
    if ctl_fd is None:
      self.fd = ctl_fd = os.open("/dev/snd/controlC%i" % card, os.O_RDONLY)
    else:
      self.fd = os.dup(ctl_fd)
    info = struct.pack('ii16s16s32s80s16s80s128s', 0, 0, '', '', '', '', '', '', '')
    res = ioctl(ctl_fd, CTL_IOCTL_CARD_INFO, info)
    a = struct.unpack('ii16s16s32s80s16s80s128s', res)
    self.id = a[2].replace('\x00', '')
    self.driver = a[3].replace('\x00', '')
    self.name = a[4].replace('\x00', '')
    self.longname = a[5].replace('\x00', '')
    self.components = a[8].replace('\x00', '')

  def __del__(self):
    if not self.fd is None:
      os.close(self.fd)

class HDACodec:

  afg = None
  mfg = None
  vendor_id = None
  subsystem_id = None
  revision_id = None

  def __init__(self, card=0, device=0, clonefd=None):
    self.fd = None
    self.hwaccess = True
    ctl_fd = None
    self.exporter = None
    self.exporta = []
    if type(1) == type(card):
      self.device = device
      self.card = card
      self.mcard = HDACard(card)
      ctl_fd = self.mcard.fd
    else:
      self.device = device
      self.mcard = card
      self.card = card.card
    if not clonefd:
      self.fd = os.open("/dev/snd/hwC%sD%s" % (card, device), os.O_RDWR)
    else:
      self.fd = os.dup(clonefd)
    info = struct.pack('Ii64s80si64s', 0, 0, '', '', 0, '')
    res = ioctl(self.fd, IOCTL_INFO, info)
    name = struct.unpack('Ii64s80si64s', res)[3]
    if not name.startswith('HDA Codec'):
      raise IOError, "unknown HDA hwdep interface"
    res = ioctl(self.fd, IOCTL_PVERSION, struct.pack('I', 0))
    self.version = struct.unpack('I', res)
    if self.version < 0x00010000:	# 1.0.0
      raise IOError, "unknown HDA hwdep version"
    self.mixer = AlsaMixer(self.card, ctl_fd=ctl_fd)
    self.parse_proc()

  def __del__(self):
    if not self.fd is None:
      os.close(self.fd)

  def rw(self, nid, verb, param):
    """do elementary read/write operation"""
    if not self.exporter:
      verb = (nid << 24) | (verb << 8) | param
      res = ioctl(self.fd, IOCTL_VERB_WRITE, struct.pack('II', verb, 0))
      return struct.unpack('II', res)[1]
    else:
      return self.exporter.rw(self.exporta and self.exporta[-1] or False, nid, verb, param)
    
  def get_wcap(self, nid):
    """get cached widget capabilities"""
    res = ioctl(self.fd, IOCTL_GET_WCAPS, struct.pack('II', nid << 24, 0))
    return struct.unpack('II', res)[1]

  def get_raw_wcap(self, nid):
    """get raw widget capabilities"""
    return self.rw(nid, VERBS['PARAMETERS'], PARAMS['AUDIO_WIDGET_CAP'])

  def param_read(self, nid, param):
    """read perameters"""
    return self.rw(nid, VERBS['PARAMETERS'], param)

  def get_sub_nodes(self, nid):
    """return sub-nodes count (returns count and start NID)"""
    res = self.param_read(nid, PARAMS['NODE_COUNT'])
    return res & 0x7fff, (res >> 16) & 0x7fff

  def get_connections(self, nid):
    """parses connection list and returns the array of NIDs"""
    parm = self.param_read(nid, PARAMS['CONNLIST_LEN'])
    if parm & (1 << 7):		# long
      shift = 16
      num_elems = 2
    else:			# short
      shift = 8
      num_elems = 4
    conn_len = parm & 0x7f
    mask = (1 << (shift - 1)) - 1
    if not conn_len:
      return None
    if conn_len == 1:
      parm = self.rw(nid, VERBS['GET_CONNECT_LIST'], 0)
      return [parm & mask]
    res = []
    prev_nid = 0
    for i in range(conn_len):
      if i % num_elems == 0:
        parm = self.rw(nid, VERBS['GET_CONNECT_LIST'], i)
      range_val = parm & (1 << (shift - 1))
      val = parm & mask
      parm >>= shift
      if range_val:
        if not prev_nid or prev_nid >= val:
          raise IOError, "invalid dep_range_val 0x%x:0x%x\n" % (prev_nid, val)
        n = prev_nid + 1
        while n <= val:
          res.append(n)
          n += 1
      else:
        res.append(val)
      prev_nid = val
    return res

  def revert(self):
    if not self.gpio is None:
      self.gpio.revert()
    for nid in self.nodes:
      self.nodes[nid].revert()

  def export_start(self, mode):
    self.exporta.append(mode)

  def export_end(self):
    self.exporta.pop()

  def export(self, exporter):
    self.exporter = exporter
    if not self.gpio is None:
      self.gpio.export()
    for nid in self.nodes:
      self.nodes[nid].export()
    self.exporter = None

  def get_node(self, nid):
    if nid == self.afg:
      return HDARootNode(self, "Audio Root Node")
    return self.nodes[nid]

  def parse_proc(self):
    from hda_proc import HDACodecProc, DecodeProcFile
    file = "/proc/asound/card%i/codec#%i" % (self.card, self.device)
    if os.path.exists(file):
      file = DecodeProcFile(file)
      self.proc_codec = HDACodecProc(self.card, self.device, file)
    else:
      self.proc_codec = None
      print "Unable to find proc file '%s'" % file

  def analyze(self):
    self.afg = None
    self.mfg = None
    self.nodes = {}
    self.gpio = None
    self.afg_function_id = 0			# invalid
    self.mfg_function_id = 0			# invalid
    self.afg_unsol = 0
    self.mfg_unsol = 0
    self.vendor_id = self.param_read(AC_NODE_ROOT, PARAMS['VENDOR_ID'])
    self.subsystem_id = self.param_read(AC_NODE_ROOT, PARAMS['SUBSYSTEM_ID'])
    self.revision_id = self.param_read(AC_NODE_ROOT, PARAMS['REV_ID'])
    self.name = "0x%08x" % self.vendor_id	# FIXME
    self.pcm_rates = []
    self.pcm_bits = []
    self.pcm_streams = []
    self.amp_caps_in = None
    self.amp_caps_out = None
    self.gpio_max = 0
    self.gpio_o = 0
    self.gpio_i = 0
    self.gpio_unsol = 0
    self.gpio_wake = 0

    total, nid = self.get_sub_nodes(AC_NODE_ROOT)
    for i in range(total):
      func = self.param_read(nid, PARAMS['FUNCTION_TYPE'])
      if (func & 0xff) == 0x01:		# audio group
        self.afg_function_id = func & 0xff
        self.afg_unsol = (func & 0x100) and True or False
        self.afg = nid
      elif (func & 0xff) == 0x02:	# modem group
        self.mfg_function_id = func & 0xff
        self.mfg_unsol = (func & 0x100) and True or False
        self.mfg = nid
      else:
        break
      nid += 1

    if self.subsystem_id == 0:
      self.subsystem_id = self.rw(self.afg and self.afg or self.mfg,
                                  VERBS['GET_SUBSYSTEM_ID'], 0)

    # parse only audio function group
    if self.afg == None:
      return

    pcm = self.param_read(self.afg, PARAMS['PCM'])
    self.pcm_rate = pcm & 0xffff
    self.pcm_rates = self.analyze_pcm_rates(self.pcm_rate)
    self.pcm_bit = pcm >> 16
    self.pcm_bits = self.analyze_pcm_bits(self.pcm_bit)

    self.pcm_stream = self.param_read(self.afg, PARAMS['STREAM'])
    self.pcm_streams = self.analyze_pcm_streams(self.pcm_stream)

    self.amp_caps_in = HDAAmpCaps(self, self.afg, HDA_INPUT)
    self.amp_caps_out = HDAAmpCaps(self, self.afg, HDA_OUTPUT)

    self.gpio_cap = self.param_read(self.afg, PARAMS['GPIO_CAP'])
    self.gpio_max = self.gpio_cap & 0xff
    self.gpio_o = (self.gpio_cap >> 8) & 0xff
    self.gpio_i = (self.gpio_cap >> 16) & 0xff
    self.gpio_unsol = (self.gpio_cap >> 30) & 1 and True or False
    self.gpio_wake = (self.gpio_cap >> 31) & 1 and True or False
    self.gpio = HDAGPIO(self, self.afg)

    nodes_count, nid = self.get_sub_nodes(self.afg)
    self.base_nid = nid
    for i in range(nodes_count):
      self.nodes[nid] = HDANode(self, nid)
      nid += 1

  def reread(self):
    if not self.gpio is None:
      self.gpio.reread()
    for node in self.nodes:
      self.nodes[node].reread()

  def analyze_pcm_rates(self, pcm):
    rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200,
             96000, 176400, 192000, 384000]
    res = []
    for i in range(len(rates)):
      if pcm & (1 << i):
        res.append(rates[i])
    return res

  def analyze_pcm_bits(self, bit):
    bits = [8, 16, 20, 24, 32]
    res = []
    for i in range(len(bits)):
      if bit & (1 << i):
        res.append(bits[i])
    return res

  def analyze_pcm_streams(self, stream):
    res = []
    if stream & 0x01: res.append("PCM")
    if stream & 0x02: res.append("FLOAT")
    if stream & 0x04: res.append("AC3")
    return res

  def dump(self, skip_nodes=False):

    def print_pcm_rates(node):
      s = ''
      for i in node.pcm_rates:
        s += " %d" % i
      return "    rates [0x%x]:%s\n" % (node.pcm_rate, s)
      
    def print_pcm_bits(node):
      s = ''
      for i in node.pcm_bits:
        s += " %d" % i
      return "    bits [0x%x]:%s\n" % (node.pcm_bit, s)
    
    def print_pcm_formats(node):
      str = "    formats [0x%x]:" % node.pcm_stream
      for i in node.pcm_streams:
        str += " %s" % i
      return str + "\n"

    def print_pcm_caps(node):
      str = print_pcm_rates(node)
      str += print_pcm_bits(node)
      return str + print_pcm_formats(node)
      
    def print_gpio(node):
      gpio = node.gpio_cap
      str = 'GPIO: io=%d, o=%d, i=%d, unsolicited=%d, wake=%d\n' % \
            (node.gpio_max, node.gpio_o, node.gpio_i,
             node.gpio_unsol and 1 or 0, node.gpio_wake and 1 or 0)
      for i in range(node.gpio_max):
        str += '  IO[%d]: enable=%d, dir=%d, wake=%d, sticky=%d, ' \
               'data=%d, unsol=%d\n' % (i, 
                node.gpio.test('enable', i) and 1 or 0,
                node.gpio.test('direction', i) and 1 or 0,
                node.gpio.test('wake', i) and 1 or 0,
                node.gpio.test('sticky', i) and 1 or 0,
                node.gpio.test('data', i) and 1 or 0,
                node.gpio.test('unsol', i) and 1 or 0)
      return str

    def print_amp_caps(caps):
      if caps.ofs == None:
        return "N/A\n"
      return "ofs=0x%02x, nsteps=0x%02x, stepsize=0x%02x, mute=%x\n" % \
              (caps.ofs, caps.nsteps, caps.stepsize, caps.mute and 1 or 0)

    if not self.afg and not self.mfg:
      self.analyze()
    str = 'Codec: %s\n' % self.name
    str += 'Address: %i\n' % self.device
    if not self.afg is None:
      str += 'AFG Function Id: 0x%x (unsol %u)\n' % (self.afg_function_id, self.afg_unsol)
    if not self.mfg is None:
      str += 'MFG Function Id: 0x%x (unsol %u)\n' % (self.mfg_function_id, self.mfg_unsol)
    str += 'Vendor Id: 0x%x\n' % self.vendor_id
    str += 'Subsystem Id: 0x%x\n' % self.subsystem_id
    str += 'Revision Id: 0x%x\n' % self.revision_id
    if self.mfg:
      str += 'Modem Function Group: 0x%x\n' % self.mfg
    else:
      str += 'No Modem Function Group found\n'
    if self.afg is None: return str
    str += 'Default PCM:\n'
    str += print_pcm_caps(self)
    str += 'Default Amp-In caps: '
    str += print_amp_caps(self.amp_caps_in)
    str += 'Default Amp-Out caps: '
    str += print_amp_caps(self.amp_caps_out)
    
    if self.base_nid == 0 or self.nodes < 0:
      str += 'Invalid AFG subtree\n'
      return str
    
    str += print_gpio(self)

    if not skip_nodes:
      for i in self.nodes:
        str += self.dump_node(self.nodes[i])
    
    return str

  def dump_node(self, node):

    def print_pcm_rates(node):
      s = ''
      for i in node.pcm_rates:
        s += " %d" % i
      return "    rates [0x%x]:%s\n" % (node.pcm_rate, s)
      
    def print_pcm_bits(node):
      s = ''
      for i in node.pcm_bits:
        s += " %d" % i
      return "    bits [0x%x]:%s\n" % (node.pcm_bit, s)
    
    def print_pcm_formats(node):
      str = "    formats [0x%x]:" % node.pcm_stream
      for i in node.pcm_streams:
        str += " %s" % i
      return str + "\n"

    def print_pcm_caps(node):
      str = print_pcm_rates(node)
      str += print_pcm_bits(node)
      return str + print_pcm_formats(node)
      
    def print_audio_io(node):
      str = "  Converter: stream=%d, channel=%d\n" % (node.aud_stream, node.aud_channel)
      if node.sdi_select != None:
        str += "  SDI-Select: %d\n" % node.sdi_select
      return str
      
    def print_amp_caps(caps):
      if caps.ofs == None:
        return "N/A\n"
      return "ofs=0x%02x, nsteps=0x%02x, stepsize=0x%02x, mute=%x\n" % \
              (caps.ofs, caps.nsteps, caps.stepsize, caps.mute and 1 or 0)

    def print_amp_vals(vals):
      str = ''
      idx = 0
      for val in vals.vals:
        if vals.stereo and (idx & 1) == 0:
          str += " [0x%02x" % val
        else:
          str += " 0x%02x" % val
        if vals.stereo and (idx & 1) != 0: str += "]"
        idx += 1
      return str + '\n'
      
    def print_pin_caps(node):
      str = "  Pincap 0x%08x:" % node.pincaps
      if 'IN' in node.pincap: str += " IN"
      if 'OUT' in node.pincap: str += " OUT"
      if 'HP_DRV' in node.pincap: str += " HP"
      if 'EAPD' in node.pincap: str += " EAPD"
      if 'PRES_DETECT' in node.pincap: str += " Detect"
      if 'BALANCE' in node.pincap: str += " Balance"
      if 'HDMI' in node.pincap:
        if (self.vendor_id >> 16) == 0x10ec:	# Realtek has different meaning
          str += " (Realtek)R/L"
        else:
          if 'HBR' in node.pincap:
            str += " HBR"
          str += " HDMI"
      if 'DP' in node.pincap: str += " DP"
      if 'TRIG_REQ' in node.pincap: str += " Trigger"
      if 'IMP_SENSE' in node.pincap: str += " ImpSense"
      str += '\n'
      if node.pincap_vref:
        str += "    Vref caps:"
        if 'HIZ' in node.pincap_vref: str += " HIZ"
        if '50' in node.pincap_vref: str += " 50"
        if 'GRD' in node.pincap_vref: str += " GRD"
        if '80' in node.pincap_vref: str += " 80"
        if '100' in node.pincap_vref: str += " 100"
        str += '\n'
      if 'EAPD' in node.pincap:
        str += "  EAPD 0x%x:" % node.pincap_eapdbtls
        if 'BALANCED' in node.pincap_eapdbtl: str += " BALANCED"
        if 'EAPD' in node.pincap_eapdbtl: str += " EAPD"
        if 'LR_SWAP' in node.pincap_eapdbtl: str += " R/L"
        str += '\n'
      str += "  Pin Default 0x%08x: [%s] %s at %s %s\n" % (node.defcfg_pincaps,
              node.jack_conn_name,
              node.jack_type_name,
              node.jack_location_name,
              node.jack_location2_name)
      str += "    Conn = %s, Color = %s\n" % (node.jack_connector_name,
              node.jack_color_name)
      str += "    DefAssociation = 0x%x, Sequence = 0x%x\n" % \
              (node.defcfg_assoc, node.defcfg_sequence)
      if 'NO_PRESENCE' in node.defcfg_misc:
        str += "    Misc = NO_PRESENCE\n"
      if node.pinctl:
        str += "  Pin-ctls: 0x%02x:" % node.pinctls
        if 'IN' in node.pinctl: str += " IN"
        if 'OUT' in node.pinctl: str += " OUT"
        if 'HP' in node.pinctl: str += " HP"
        if node.pincap_vref:
          str += " VREF_%s" % node.pinctl_vref
        str += '\n'
      return str

    def print_vol_knob(node):
      str = "  Volume-Knob: delta=%d, steps=%d, " % (node.vol_knb_delta, node.vol_knb_steps)
      return str + "direct=%d, val=%d\n" % (node.vol_knb_direct, node.vol_knb_val)

    def print_unsol_cap(node):
      return "  Unsolicited: tag=0x%02x, enabled=%d\n" % (node.unsol_tag, node.unsol_enabled and 1 or 0)

    def print_power_state(node):
      str = ""
      if node.pwr_states:
        str = "  Power states: %s\n" % ' '.join(node.pwr_states)
      return "  Power: setting=%s, actual=%s\n" % (node.pwr_setting_name, node.pwr_actual_name)

    def print_digital_conv(node):
      str = "  Digital:"
      if 'ENABLE' in node.dig1: str += " Enabled"
      if 'VALIDITY' in node.dig1: str += " Validity"
      if 'VALIDITYCFG' in node.dig1: str += " ValidityCfg"
      if 'EMPHASIS' in node.dig1: str += " Preemphasis"
      if 'COPYRIGHT' in node.dig1: str += " Copyright"
      if 'NONAUDIO' in node.dig1: str += " Non-Audio"
      if 'PROFESSIONAL' in node.dig1: str += " Pro"
      if 'GENLEVEL' in node.dig1: str += " GetLevel"
      str += "\n"
      return str + "  Digital category: 0x%x\n" % ((node.dig1_category >> 8) & 0x7f)

    def print_conn_list(node):
      str = "  Connection: %d\n" % (node.connections and len(node.connections) or 0)
      if node.connections:
        str += "    "
        for i in range(len(node.connections)):
          str += " 0x%02x" % node.connections[i]
          if i == node.active_connection and len(node.connections) > 1:
            str += "*"
        str += '\n'
      return str

    def print_proc_caps(node):
      return "  Processing caps: benign=%d, ncoeff=%d\n" % (node.proc_benign, node.proc_numcoef)

    def print_realtek_coef(node):
      str = "  Processing Coefficient: 0x%02x\n" % node.realtek_coeff_proc
      return str + "  Coefficient Index: 0x%02x\n" % node.realtek_coeff_index

    str = "Node 0x%02x [%s] wcaps 0x%x:" % (node.nid, node.wtype_name(), node.wcaps)
    if node.stereo:
      str += node.channels == 2 and " Stereo" or " %d-Channels" % node.channels
    else:
      str += " Mono"
    if node.digital: str += " Digital"
    if node.in_amp: str += " Amp-In"
    if node.out_amp: str += " Amp-Out"
    if node.stripe: str += " Stripe"
    if node.lr_swap: str += " R/L"
    if node.cp_caps: str += " CP"
    str += '\n'
    str += self.dump_node_extra(node)
    if node.in_amp:
      str += "  Amp-In caps: "
      str += print_amp_caps(node.amp_caps_in)
      str += "  Amp-In vals:"
      str += print_amp_vals(node.amp_vals_in)
    if node.out_amp:
      str += "  Amp-Out caps: "
      str += print_amp_caps(node.amp_caps_out)
      str += "  Amp-Out vals:"
      str += print_amp_vals(node.amp_vals_out)
      
    if node.wtype_id == 'PIN':
      str += print_pin_caps(node)
    elif node.wtype_id == 'VOL_KNB':
      str += print_vol_knob(node)
    elif node.wtype_id in ['AUD_IN', 'AUD_OUT']:
      str += print_audio_io(node)
      if node.digital:
        str += print_digital_conv(node)
      if node.format_ovrd:
        str += "  PCM:\n"
        str += print_pcm_caps(node)
    if node.unsol_cap:
      str += print_unsol_cap(node)
    if node.power:
      str += print_power_state(node)
    if node.wdelay:
      str += "  Delay: %d samples\n" % node.wdelay
    if node.conn_list:
      str += print_conn_list(node)
    if node.proc_wid:
      str += print_proc_caps(node)
    if hasattr(node, 'realtek_coeff_proc'):
      str += print_realtek_coef(node)
    return str

  def dump_node_extra(self, node):
    if self.proc_codec:
      return self.proc_codec.dump_node_extra(node)
    return ''

  def get_device(self, nid):
    if self.proc_codec:
      return self.proc_codec.get_device(nid)
    return None

  def get_controls(self, nid):
    if self.proc_codec:
      return self.proc_codec.get_controls(nid)
    return None

  def connections(self, nid, dir=0):
    if dir == 0:
      if nid in self.nodes:
        conn = self.nodes[nid].connections
        if conn:
          return len(conn)
      return 0
    res = 0
    for nid in self.nodes:
      node = self.nodes[nid]
      if nid != nid and node.connections and nid in node.connections:
        res += 1
    return res

  def graph(self, dump=False, prefer_x=None, prefer_y=None):
  
    def mfind(nid):
      for y in range(len(res)):
        if nid in res[y]:
          return (y, res[y].index(nid))
      return None, None

    def doplace(nid, y, x):
      node = self.nodes[nid]
      if node.wtype_id == 'AUD_MIX':
        if y == 0:
          y += 1
        while 1:
          x += 1
          if x >= len(res[0]) - 1:
            x = 1
            y += 1
          if y >= len(res) - 1:
            return False
          if res[y][x+1] is None and \
             res[y][x-1] is None and \
             res[y+1][x] is None and \
             res[y-1][x] is None and \
             res[y][x] is None:
            res[y][x] = nid
            return True
      if y == 0:
        for idx in range(len(res)-2):
          if res[idx+1][x] is None:
            res[idx+1][x] = nid
            return True
      elif y == len(res)-1:
        for idx in reversed(range(len(res)-2)):
          if res[idx+1][x] is None:
            res[idx+1][x] = nid
            return True
      elif x == 0:
        for idx in range(len(res[0])-2):
          if res[y][idx+1] is None:
            res[y][idx+1] = nid
            return True
      elif x == len(res)-1:
        for idx in range(len(res[0])-2):
          if res[y][idx+1] is None:
            res[y][idx+1] = nid
            return True
      else:
        if y+1 < len(res) and res[y+1][x] is None:
          res[y+1][x] = nid
          return True
        if y-1 != 0 and res[y-1][x] is None:
          res[y-1][x] = nid
          return True
        if x+1 < len(res[0]) and res[y][x+1] is None:
          res[y][x+1] = nid
          return True
        if x-1 != 0 and res[y][x-1] is None:
          res[y][x-1] = nid
          return True
        if y+1 < len(res):
          return doplace(nid, y+1, 1)
        if x+1 < len(res[0]):
          return doplace(nid, 1, x+1)
        return False
      return None

    error = 0
    res = []
    unplaced = []
    # determine all termination widgets
    terms = {'AUD_IN':[], 'AUD_OUT':[], 'PIN_IN':[], 'PIN_OUT':[]}
    mixes = 0
    for nid in self.nodes:
      node = self.nodes[nid]
      if node.wtype_id == 'AUD_MIX':
        mixes += 1
      if node.wtype_id in ['AUD_IN', 'AUD_OUT', 'PIN']:
        id = node.wtype_id
        if id == 'PIN':
          id = 'IN' in node.pinctl and 'PIN_IN' or 'PIN_OUT'
        terms[id].append(nid)
      else:
        unplaced.append(nid)
    for id in terms:
      terms[id].sort()
    # build the matrix
    if prefer_x:
      x = prefer_x
    else:
      x = max(len(terms['AUD_IN']), len(terms['AUD_OUT'])) + 2
    if prefer_y:
      y = prefer_y
    else:
      y = max(len(terms['PIN_IN']), len(terms['PIN_OUT'])) + 2
    if x <= 2 and y <= 2:
      return None
    while (x - 2) * (y - 2) < mixes * 9:
      if x <= y:
        x += 1
      else:
        y += 1
    for a in range(y):
      res.append([None]*x)
    if 'PIN_IN' in terms:
      for idx in range(len(terms['PIN_IN'])):
        res[idx+1][0] = terms['PIN_IN'][idx]
    if 'PIN_OUT' in terms:
      for idx in range(len(terms['PIN_OUT'])):
        res[idx+1][-1] = terms['PIN_OUT'][idx]
    if 'AUD_IN' in terms:
      idx = 1
      for nid in terms['AUD_IN']:
        res[0][idx] = nid
        idx += 1
    if 'AUD_OUT' in terms:
      idx = 1
      for nid in terms['AUD_OUT']:
        res[-1][idx] = nid
        idx += 1
    # check and resize the matrix for unplaced nodes
    while len(res)**len(res[0]) < len(unplaced):
      res.insert(-2, [None]*x)
    # assign unplaced nids - check connections
    unplaced.sort()
    while unplaced and not error:
      change = len(unplaced)
      for idx in range(len(res)):
        for idx1 in range(len(res[idx])):
          nid = res[idx][idx1]
          if nid is None:
            continue
          node = self.nodes[nid]
          if not node or not node.connections:
            continue
          for conn in node.connections:
            if conn in unplaced:
              pl = doplace(conn, idx, idx1)
              if pl is True:
                unplaced.remove(conn)
              elif pl is None:
                error += 1
                break
      if error:
        break
      for nid in unplaced:
        node = self.nodes[nid]
        if not node.connections:
          continue
        for conn in node.connections:
          placed = False
          y, x = mfind(nid)
          if not y or not x:
            continue
          pl = doplace(nid, y, x)
          if pl is True:
            unplaced.remove(nid)
            break
          elif pl is None:
            error += 1
            break
        if error:
          break
      if len(unplaced) == change:
        break
    y = len(res)
    x = 0
    for nid in unplaced:
      if y >= len(res):
        res.append([None]*len(res[0]))
      res[y][x] = nid
      x += 1
      if x >= len(res[0]):
        y += 1
        x = 0
    if error:
      return self.graph(dump=dump, prefer_x=x+2, prefer_y=y+2)
    # do extra check
    check = []
    for y in range(len(res)):
      for x in range(len(res[0])):
        nid = res[y][x]
        if not nid is None:
          if nid in check:
            raise ValueError, "double nid in graph matrix"
          if not nid in self.nodes:
            raise ValueError, "unknown nid in graph matrix"
          check.append(nid)
    if len(check) != len(self.nodes):
      raise ValueError, "not all nids in graph matrix"
    # do addition dump
    if dump:
      print "****", len(self.nodes)
      for nodes in res:
        str = ''
        for node2 in nodes:
          str += node2 is None and '--  ' or '%02x  ' % node2
        print str
      print "****"
    return res

class HDA_Exporter_pyscript:

  def __init__(self):
    self.old_verbs = {}
    self.new_verbs = {}

  def title(self):
    return 'Export to Python Script'

  def stitle(self):
    return "pyscript"
    
  def rw(self, old, nid, verb, param):
    if verb & 0x0800:
      raise ValueError, "read: nid=0x%x, verb=0x%x, param=0x%x" % (nid, verb, param)
    #print "old = 0x%x, nid = 0x%x, verb = 0x%x, param = 0x%x" % (old, nid, verb, param)
    verb |= param >> 8
    if old:
      if not nid in self.old_verbs:
        self.old_verbs[nid] = {}
      self.old_verbs[nid][verb] = param
    else:
      if not nid in self.new_verbs:
        self.new_verbs[nid] = {}
      self.new_verbs[nid][verb] = param

  def text(self, codec):
    text = ''
    nids = self.new_verbs.keys()[:]
    for nid in nids:
      for verb in self.new_verbs[nid]:
        old = self.old_verbs[nid][verb]
        new = self.new_verbs[nid][verb]
        if old != new:
          verb1 = verb & ~(new >> 8)
          pack = (nid << 24) | (verb << 8) | new
          for k, v in VERBS.items():
            if v == verb1:
              txt = k
              break
          s1 = new < 256 and ("  0x%02x" % new) or ("0x%04x" % new)
          text += "set(0x%02x, 0x%03x, %s) # 0x%08x (%s)\n" % (nid, verb1, s1, pack, txt)
    if not text:
      text = '# no change'
    else:
      text = """\
#!/usr/bin/env python

import os
import struct
from fcntl import ioctl

def __ioctl_val(val):
  # workaround for OverFlow bug in python 2.4
  if val & 0x80000000:
    return -((val^0xffffffff)+1)
  return val

IOCTL_INFO = __ioctl_val(0x80dc4801)
IOCTL_PVERSION = __ioctl_val(0x80044810)
IOCTL_VERB_WRITE = __ioctl_val(0xc0084811)

def set(nid, verb, param):
  verb = (nid << 24) | (verb << 8) | param
  res = ioctl(FD, IOCTL_VERB_WRITE, struct.pack('II', verb, 0))  

FD = os.open("%s", os.O_RDONLY)
info = struct.pack('Ii64s80si64s', 0, 0, '', '', 0, '')
res = ioctl(FD, IOCTL_INFO, info)
name = struct.unpack('Ii64s80si64s', res)[3]
if not name.startswith('HDA Codec'):
  raise IOError, "unknown HDA hwdep interface"
res = ioctl(FD, IOCTL_PVERSION, struct.pack('I', 0))
version = struct.unpack('I', res)
if version < 0x00010000:	# 1.0.0
  raise IOError, "unknown HDA hwdep version"

# initialization sequence starts here...

%s
os.close(FD)
""" % ("/dev/snd/hwC%sD%s" % (codec.card, codec.device), text)
    return text

def HDA_card_list():
  from dircache import listdir
  result = []
  for name in listdir('/dev/snd/'):
    if name.startswith('controlC'):
      try:
	fd = os.open("/dev/snd/%s" % name, os.O_RDONLY)
      except OSError, msg:
      	continue
      info = struct.pack('ii16s16s32s80s16s80s128s', 0, 0, '', '', '', '', '', '', '')
      res = ioctl(fd, CTL_IOCTL_CARD_INFO, info)
      a = struct.unpack('ii16s16s32s80s16s80s128s', res)
      card = a[0]
      components = a[8].replace('\x00', '')
      if components.find('HDA:') >= 0:
        result.append(HDACard(card, ctl_fd=fd))
      os.close(fd)
  return result

if __name__ == '__main__':
  v = HDACodec()
  v.analyze()
  print "vendor_id = 0x%x, subsystem_id = 0x%x, revision_id = 0x%x" % (v.vendor_id, v.subsystem_id, v.revision_id)
  print "afg = %s, mfg = %s" % (v.afg and "0x%x" % v.afg or 'None', v.mfg and "0x%x" % v.mfg or 'None')
  print
  print
  print v.dump()[:-1]
