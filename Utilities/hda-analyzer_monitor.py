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

import gobject
import gtk
import pango
from errno import EAGAIN
from subprocess import Popen, PIPE, STDOUT
from fcntl import fcntl, F_SETFL, F_GETFL
from signal import SIGKILL
import os

CHANNELS = [
  "Front Left",
  "Front Right",
  "Rear Left",
  "Rear Right",
  "Center",
  "LFE/Woofer",
  "Side Left",
  "Side Right"
]

def set_fd_nonblocking(fd):
   flags = fcntl(fd, F_GETFL)
   fcntl(fd, F_SETFL, flags | os.O_NONBLOCK)

class Monitor(gtk.Window):

  channel = 0
  channels = 0
  device = ''
  generate_num = 0

  def __init__(self, parent=None, device=None):
    self.device = device
    if not self.device:
      self.device = 'plughw:0'
    gtk.Window.__init__(self)
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      pass
    self.connect('destroy', self.__destroy)
    self.set_default_size(600, 400)
    self.set_title(self.__class__.__name__)
    self.set_border_width(10)
    vbox = gtk.VBox(False, 0)
    text_view = gtk.TextView()
    fontName = pango.FontDescription("Misc Fixed,Courier 10")
    text_view.modify_font(fontName)
    text_view.set_border_width(4)
    text_view.set_size_request(580, 350)
    buffer = gtk.TextBuffer(None)
    self.info_buffer = buffer
    iter = buffer.get_iter_at_offset(0)
    buffer.insert(iter, 'Please, select channel to play or number channels to record...')
    text_view.set_buffer(buffer)
    text_view.set_editable(False)
    text_view.set_cursor_visible(False)
    vbox.pack_start(text_view)
    self.statusbar = gtk.Statusbar()
    vbox.pack_start(self.statusbar, True, False)
    separator = gtk.HSeparator()
    vbox.pack_start(separator, expand=False)
    frame = gtk.Frame('Playback')
    frame.set_border_width(4)
    hbox = gtk.HBox(False, 0)
    hbox.set_border_width(4)
    idx = 0
    for name in CHANNELS:
      button = gtk.Button(name)
      button.connect("clicked", self.__channel_change, idx)
      hbox.pack_start(button, False, False)
      idx += 1
    frame.add(hbox)
    vbox.pack_start(frame, False, False)
    frame = gtk.Frame('Capture')
    frame.set_border_width(4)
    hbox = gtk.HBox(False, 0)
    hbox.set_border_width(4)
    for idx in [2, 4, 6, 8]:
      button = gtk.Button("%s channels" % idx)
      button.connect("clicked", self.__channels_change, idx)
      hbox.pack_start(button, False, False)
      idx += 1
    frame.add(hbox)
    vbox.pack_start(frame, False, False)
    self.add(vbox)
    self.generate_p = None
    self.record_p = None
    self.set_title('ALSA Monitor for %s' % self.device)
    self.show_all()

  def __destroy(self, e):
    self.generate_cleanup()
    self.record_cleanup()
    gtk.main_quit()

  def __channel_change(self, button, idx):
    if self.channel != idx or self.generate_p == None:
      self.set_text('Switching to playback...')
      self.channel = idx
      self.record_cleanup()
      self.generate_cleanup()
      self.generate_sound()

  def __channels_change(self, button, idx):
    if self.channels != idx or self.record_p == None:
      self.set_text('Switching to record...')
      self.channels = idx
      self.generate_cleanup()
      self.record_cleanup()
      self.record_sound()

  def set_text(self, text):
    buffer = self.info_buffer
    start, end = buffer.get_bounds()
    buffer.delete(start, end)
    if not text: return
    iter = buffer.get_iter_at_offset(0)
    buffer.insert(iter, text)

  def set_status(self, text):
    context_id = self.statusbar.get_context_id("SCTX")
    self.statusbar.pop(context_id)
    self.statusbar.push(context_id, text)

  def generate_sound(self):
    self.set_status('Playing sound #%s on channel %s...' % \
    			(self.generate_num, CHANNELS[self.channel]))
    self.generate_num += 1
    channels = 2
    if self.channel >= 6:
      channels = 8
    elif self.channel >= 4:
      channels = 6
    elif self.channel >= 2:
      channels = 4
    self.cmd = ["speaker-test", "-D", self.device,
	       "-c", str(channels),
	       "-s", str(self.channel + 1)]
    p = Popen(self.cmd,
    	      shell=False, bufsize=0, stdin=None, stdout=PIPE, stderr=PIPE,
	      close_fds=True)
    for fd in [p.stdout.fileno(), p.stderr.fileno()]:
      set_fd_nonblocking(fd)
    self.generate_p = p
    self.generate_stdout_id = gobject.io_add_watch(p.stdout, gobject.IO_IN|gobject.IO_HUP|gobject.IO_NVAL, self.generate_io_stdout)
    self.generate_stderr_id = gobject.io_add_watch(p.stderr, gobject.IO_IN|gobject.IO_HUP|gobject.IO_NVAL, self.generate_io_stderr)
    self.generate_timeout_id = gobject.timeout_add(5000, self.generate_timeout)
    self.generate_stdout = ''
    self.generate_stderr = ''

  def generate_cleanup(self):
    if not self.generate_p:
      return
    if self.generate_p.poll() == None:
      try:
        os.kill(self.generate_p.pid, SIGKILL)
      except:
      	pass
    self.generate_p.wait()
    gobject.source_remove(self.generate_timeout_id)
    gobject.source_remove(self.generate_stdout_id)
    gobject.source_remove(self.generate_stderr_id)
    del self.generate_p
    self.generate_p = None

  def generate_timeout(self):
    if self.generate_stdout == '' or self.generate_p.poll() != None:
      if self.generate_stdout == '':
      	self.set_text('Cannot play. Device is busy...')
      else:
      	self.set_text(' '.join(self.cmd) + '\n\n' + self.generate_stdout)
      self.generate_cleanup()
      self.generate_sound()
      return False    
    return True

  def generate_io_stdout(self, source, condition):
    if condition & gobject.IO_IN:
      self.generate_stdout += source.read(1024)
      self.set_text(' '.join(self.cmd) + '\n\n' + self.generate_stdout)
      return True

  def generate_io_stderr(self, source, condition):
    if condition & gobject.IO_IN:
      self.generate_stderr += source.read(1024)
      return True

  def record_sound(self):
    self.set_status('Recording sound - %s channels...' % self.channels)
    self.cmd = ["arecord", "-D", self.device,
	       "-f", "dat", "-c", str(self.channels),
	       "-t", "raw", "-vvv", "/dev/null"]
    p = Popen(self.cmd,
    	      shell=False, bufsize=0, stdin=None, stdout=PIPE, stderr=PIPE,
	      close_fds=True)
    for fd in [p.stdout.fileno(), p.stderr.fileno()]:
      set_fd_nonblocking(fd)
    self.record_p = p
    self.record_stdout_id = gobject.io_add_watch(p.stdout, gobject.IO_IN|gobject.IO_HUP|gobject.IO_NVAL, self.record_io_stdout)
    self.record_stderr_id = gobject.io_add_watch(p.stderr, gobject.IO_IN|gobject.IO_HUP|gobject.IO_NVAL, self.record_io_stderr)
    self.record_timeout_id = gobject.timeout_add(5000, self.record_timeout)
    self.record_stdout = ''
    self.record_stderr = ''
    self.record_count = 0
    self.record_vols = []
    self.record_data = ''

  def record_cleanup(self):
    if not self.record_p:
      return
    if self.record_p.poll() == None:
      try:
        os.kill(self.record_p.pid, SIGKILL)
      except:
      	pass
    self.record_p.wait()
    gobject.source_remove(self.record_timeout_id)
    gobject.source_remove(self.record_stdout_id)
    gobject.source_remove(self.record_stderr_id)
    del self.record_p
    self.record_p = None

  def record_timeout(self):
    if self.record_count == 0 or self.record_p.poll() != None:
      if self.record_count == '':
      	self.set_text('Cannot record. Device is busy...')
      else:
      	self.set_text(' '.join(self.cmd) + '\n\n' + self.record_stdout)
      self.record_cleanup()
      self.record_sound()
      return False    
    return True

  def record_io_stdout(self, source, condition):
    if condition & gobject.IO_IN:
      while 1:
      	try:
	  data = source.read(128)
	except IOError, e:
	  if e.errno == EAGAIN:
            self.show_record_vols()
	    break
	  raise IOError, e
	self.record_data += data
	self.record_count += len(data)
	pos = self.record_data.find('\n') 
	if pos >= 0:
	  line = self.record_data[:pos]
	  self.record_data = self.record_data[pos+1:]
	  pos = line.find('%')
	  if pos >= 0:
	    pos1 = pos - 1
	    while line[pos1] >= '0' and line[pos1] <= '9':
	      pos1 -= 1
            self.record_vols.append(int(line[pos1:pos]))
            if len(self.record_vols) > 24:
              del self.record_vols[0]
	#print data
      return True

  def record_io_stderr(self, source, condition):
    if condition & gobject.IO_IN:
      self.record_stderr += source.read(1024)
      return True

  def show_record_vols(self):
    txt = 'Volume bars (# = volume, . = empty)\n'
    max = 60
    for i in self.record_vols:
      limit = (i * max) / 100
      for c in range(max):
      	txt += c < limit and '#' or '.'
      txt += '\n'
    self.set_text(txt)

def main():
  Monitor()
  gtk.main()

if __name__ == '__main__':
  main()
