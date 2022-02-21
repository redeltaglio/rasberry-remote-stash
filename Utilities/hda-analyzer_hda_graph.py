4#!/usr/bin/env python
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
from gtk import gdk
import pango
import cairo
from hda_guilib import *

from hda_codec import EAPDBTL_BITS, PIN_WIDGET_CONTROL_BITS, \
                      PIN_WIDGET_CONTROL_VREF, DIG1_BITS, GPIO_IDS, \
                      HDA_INPUT, HDA_OUTPUT

GRAPH_WINDOWS = {}

class DummyScrollEvent:

  def __init__(self, dir):
    self.direction = dir

class Node:

  def __init__(self, codec, node, x, y, nodesize, extra):
    self.codec = codec
    self.node = node
    self.extra = extra
    sx = sy = nodesize
    self.myarea = [extra+x*(sx+extra), extra+y*(sy+extra), sx, sy]
    self.src_routes = []
    self.dst_routes = []
    self.win = None

  def longdesc(self):
    return "0x%02x" % self.node.nid

  def expose(self, cr, event, graph):

    width = self.myarea[2]
    height = self.myarea[3]

    cr.select_font_face("Misc Fixed", 
                        cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(14)
    if graph.startnode == self:
      cr.set_line_width(1.8)
      cr.set_source_rgb(0, 0, 1)
    elif graph.endnode == self:
      cr.set_line_width(1.8)
      cr.set_source_rgb(1, 0, 0)
    else:
      cr.set_line_width(0.8)    
      cr.set_source_rgb(0, 0, 0)
    cr.rectangle(*self.myarea)
    cr.stroke()

    cr.set_line_width(0.4)
    cr.move_to(self.myarea[0]+5, self.myarea[1]+13)
    cr.text_path("0x%02x: %s" % (self.node.nid, self.node.wtype_id))
    cr.stroke()

    cr.set_line_width(0.2)
    cr.rectangle(self.myarea[0], self.myarea[1] + (height/4)*3, width/2, height/4)
    cr.rectangle(self.myarea[0]+width/2, self.myarea[1] + (height/4)*3, width/2, height/4)
    cr.stroke()

    cr.set_font_size(11)
    cr.move_to(self.myarea[0]+20, self.myarea[1] + (height/4)*3+15)
    cr.text_path('IN')
    cr.stroke()
    cr.move_to(self.myarea[0]+width/2+20, self.myarea[1] + (height/4)*3+15)
    cr.text_path('OUT')
    cr.stroke()

  def has_x(self, x):
    x1 = self.myarea[0]
    x2 = x1 + self.myarea[2]
    return x >= x1 and x <= x2
    
  def compressx(self, first, size):
    if self.myarea[0] > first:
      self.myarea[0] -= size

  def has_y(self, y):
    y1 = self.myarea[1]
    y2 = y1 + self.myarea[3]
    return y >= y1 and y <= y2
    
  def compressy(self, first, size):
    if self.myarea[1] > first:
      self.myarea[1] -= size

  def in_area(self, x, y):
    if x >= self.myarea[0] and \
       y >= self.myarea[1] and \
       x < self.myarea[0] + self.myarea[2] and \
       y < self.myarea[1] + self.myarea[3]:
      wherex = x - self.myarea[0]
      wherey = y - self.myarea[1]
      if wherey >= (self.myarea[3]/4) * 3:
        if wherex >= self.myarea[2]/2:
          return "dst"
        else:
          return "src"
      else:
        return "body"

  def mouse_move(self, x, y, graph):
    what = self.in_area(x, y)
    if not what is None:
      if what == "dst":
        for r in self.dst_routes:
          r.highlight = True
      elif what == "src":
        for r in self.src_routes:
          r.highlight = True
      else:
        graph.popup = self.codec.dump_node(self.node)
      return True

class Route:

  def __init__(self, codec, src_node, dst_node, routes, nodes):
    self.codec = codec
    self.src = src_node
    self.dst = dst_node
    self.lines = []
    self.wronglines = []
    self.analyze_routes(routes, nodes)
    src_node.dst_routes.append(self)
    dst_node.src_routes.append(self)
    self.highlight = False
    self.marked = False

  def shortdesc(self):
    return "0x%02x->0x%02x" % (self.src.node.nid, self.dst.node.nid)

  def longdesc(self):
    src = self.src.node
    dst = self.dst.node
    return "%s 0x%02x -> %s 0x%02x" % (src.wtype_id.replace('_', '-'),
                        src.nid, dst.wtype_id.replace('_', '-'), dst.nid)

  def statusdesc(self):

    def niceprint(prefix, val):
      if val is None:
        return prefix
      return ' ' + prefix + ' ' + val

    src = self.src.node
    dst = self.dst.node
    vals = src.get_conn_amp_vals_str(dst)
    src = "%s 0x%02x" % (src.wtype_id.replace('_', '-'), src.nid)
    dst = "%s 0x%02x" % (dst.wtype_id.replace('_', '-'), dst.nid)
    res = niceprint("SRC " + src, vals[0]) + ' -> ' + \
          niceprint("DST " + dst, vals[1])
    return res

  def expose(self, cr, event):
    width = self.src.myarea[2]
    height = self.src.myarea[3]

    if 0: # direct green lines
      cr.set_line_width(0.3)
      cr.set_source_rgb(0.2, 1.0, 0.2)
      cr.move_to(self.src.myarea[0]+(width/4)*3, self.src.myarea[1]+height)
      cr.line_to(self.dst.myarea[0]+width/4, self.dst.myarea[1]+height)
      cr.stroke()

    for line in self.lines:
      if self.marked:
        cr.set_line_width(1.8)
        cr.set_source_rgb(1, 0, 1)
      elif self.highlight:
        cr.set_line_width(1.5)
        cr.set_source_rgb(1, 0, 0)
      else:
        inactive = self.src.node.is_conn_active(self.dst.node)
        if inactive is None:
          cr.set_line_width(0.35)
          cr.set_source_rgb(0, 0, 0)
        elif inactive is False:
          cr.set_line_width(0.35)
          cr.set_source_rgb(0, 0, 1)
        else:
          cr.set_line_width(1.5)
          cr.set_source_rgb(0, 0, 1)
      cr.move_to(line[0], line[1])
      cr.line_to(line[2], line[3])
      cr.stroke()

    for line in self.wronglines:
      cr.set_line_width(1.5)
      cr.set_source_rgb(1, 0, 0)
      cr.move_to(line[0], line[1])
      cr.line_to(line[2], line[3])
      cr.stroke()

  def select_line(self, routes, nodes, possible):

    def check_dot(posx, posy, line):
      if posx == line[0] and posx == line[2]:
        if line[1] < line[3]:
          if posy >= line[1] and posy <= line[3]:
            #print "Clash1", posx, posy, line
            return True
        else:
          if posy >= line[3] and posy <= line[1]:
            #print "Clash2", posx, posy, line
            return True
      if posy == line[1] and posy == line[3]:
        if line[0] < line[2]:
          if posx >= line[0] and posx <= line[2]:
            #print "Clash3", posx, posy, line
            return True
        else:
          if posx >= line[2] and posx <= line[0]:
            #print "Clash4", posx, posy, line
            return True
      if posx == line[0] and posy == line[1]:
        #print "Clash5", posx, posy, line
        return True
      if posx == line[2] and posy == line[3]:
        #print "Clash6", posx, posy, line
        return True
      return False 

    for p in possible:
      found = False
      for route in routes:
        if found:
          break
        for line in route.lines:
          if check_dot(line[0], line[1], p) or \
             check_dot(line[2], line[3], p) or \
             check_dot(p[0], p[1], line) or \
             check_dot(p[2], p[3], line):
            #print "Found1", p
            found = True
            break
      if nodes and not found:
        x1, y1, x2, y2 = p
        if x1 > x2 or y1 > y2:
          x2, y2, x1, y1 = p
        for node in nodes:
          xx1, yy1, xx2, yy2 = node.myarea
          xx2 += xx1
          yy2 += yy1
          if x1 < xx2 and x2 >= xx1 and y1 < yy2 and y2 >= yy1:
            #print "Found2", x1, y1, x2, y2, xx1, yy1, xx2, yy2
            found = True
            break
      if not found:
        #print "OK x1=%s,y1=%s,x2=%s,y2=%s" % (p[0], p[1], p[2], p[3])
        return p

  def analyze_routes(self, routes, nodes):
    posx, posy, width, height = self.src.myarea
    dposx, dposy, dwidth, dheight = self.dst.myarea
    extra = self.src.extra
    
    possible = []
    startx = posx >= dposx and posx - extra or posx + width
    xrange = range(5, extra-1, 5)
    if posx >= dposx:
      xrange.reverse()
      a = range(width+extra+5, width+extra*2-1, 5)
      a.reverse()
      xrange = xrange + a
      for i in range(2, 10):
        a = range(width*i+extra*i+5, width*i+extra*(i+1)-1, 5)
        a.reverse()
        xrange = xrange + a
    else:
      xrange += range(width+extra+5, width+extra*2-1, 5)
      for i in range(2, 10):
        xrange += range(width*i+extra*i+5, width*i+extra*(i+1)-1, 5)
    for j in xrange:
      possible.append([startx + j, posy + height + 5,
                       startx + j, dposy + height + 5])
    sel = self.select_line(routes, None, possible)
    if not sel:
      raise ValueError, "unable to route"

    self.lines.append(sel)

  def finish(self, routes, nodes):

    if not self.lines:
      return

    posx, posy, width, height = self.src.myarea
    dposx, dposy, dwidth, dheight = self.dst.myarea
    extra = self.src.extra
    sel = self.lines[0]
    res = True

    x = posx+(width/2)
    y = posy+height
    for tryit in range(3):
      possible = []
      fixup = sel[0] > posx and -1 or 1
      r = range(tryit*extra, (tryit+1)*extra-5-1, 5)
      if tryit == 2:
        r = range(-height-extra+5, -height-5, 5)
        r.reverse()
      x1 = x + 5 + fixup
      x2 = sel[0] - fixup
      if x1 > x2:
        sub = width/2
        x1 = x + sub + fixup
        sub -= 5
      else:
        sub = 0
      for i in range(tryit*extra, (tryit+1)*extra-5-1, 5):
        possible.append([x1, sel[1]+i, x2, sel[1]+i])
      sel1 = self.select_line(routes, nodes, possible)
      if sel1:
        sel1[0] -= fixup + sub
        sel1[2] += fixup
        possible = []
        for j in range(0, width/2-10, 5):
          possible.append([sel1[0]+j, y, sel1[0]+j, sel1[1]])
        sel2 = self.select_line(routes, nodes, possible)
        if sel2:
          sel1[0] = sel2[0]
          self.lines[0][1] = sel1[1]
          self.lines.append(sel1)
          self.lines.append(sel2)
          tryit = -1
          break
    if tryit >= 0:
      self.wronglines.append([x+5, y, sel[0], sel[1]])
      print "[1] displaced route 0x%x->0x%x %s %s" % (self.src.node.nid, self.dst.node.nid, repr(self.lines[-1]), repr(sel))
      res = False

    x = dposx
    y = dposy+height
    for tryit in range(3):
      possible = []
      fixup = sel[2] > posx and -1 or 1
      r = range(tryit * extra, (tryit+1)*extra-5-1, 5)
      if tryit == 2:
        r = range(-height-extra+5, -height-5, 5)
        r.reverse()
      sub = width/2
      x1 = x + sub + fixup
      x2 = sel[2] - fixup
      if x1 < x2:
        x1 = x + 5 + fixup
        sub = 0
      else:
        sub -= 5
      for i in r:
        possible.append([x1, sel[3]+i, x2, sel[3]+i])
      sel1 = self.select_line(routes, nodes, possible)
      if sel1:
        sel1[0] -= fixup + sub
        sel1[2] += fixup
        possible = []
        for j in range(0, width/2-10, 5):
          possible.append([sel1[0]+j, y, sel1[0]+j, sel1[1]])
        sel2 = self.select_line(routes, nodes, possible)
        if sel2:
          sel1[0] = sel2[0]
          self.lines[0][3] = sel1[3]
          self.lines.append(sel1)
          self.lines.append(sel2)
          tryit = -1
          break
    if tryit >= 0:
      self.wronglines.append([x+5, y, sel[2], sel[3]])
      print "[2] displaced route 0x%x->0x%x %s %s" % (self.src.node.nid, self.dst.node.nid, repr(self.lines[-1]), repr(sel))
      res = False
      
    return res

  def has_x(self, x):
    for line in self.lines:
      if line[0] == x or line[2] == x:
        return True
    return False
    
  def compressx(self, first, size):
    idx = 0
    while idx < len(self.lines):
      line = self.lines[idx]
      if line[0] > first:
        line[0] -= size
        self.lines[idx] = line
      if line[2] > first:
        line[2] -= size
        self.lines[idx] = line
      idx += 1

  def has_y(self, y):
    for line in self.lines:
      if line[1] == y or line[3] == y:
        return True
    return False
    
  def compressy(self, first, size):
    idx = 0
    while idx < len(self.lines):
      line = self.lines[idx]
      if line[1] > first:
        line[1] -= size
        self.lines[idx] = line
      if line[3] > first:
        line[3] -= size
        self.lines[idx] = line
      idx += 1

  def in_area(self, x, y):
    for line in self.lines:
      x1, y1, x2, y2 = line
      if x1 > x2 or y1 > y2:
        x2, y2, x1, y1 = line
      if x1 == x2 and abs(x1 - x) < 3:
        if y1 <= y and y2 >= y:
          return True
      elif y1 == y2 and abs(y1 - y) < 3:
        if x1 <= x and x2 >= x:
          return True

  def mouse_move(self, x, y, graph):
    if self.in_area(x, y):
      self.highlight = True
      return True

class CodecGraphLayout(gtk.Layout):

  def __init__(self, adj1, adj2, codec, mytitle, statusbar):
    gtk.Layout.__init__(self, adj1, adj2)
    self.set_events(0)
    self.add_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.POINTER_MOTION_MASK |
                    gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK |
                    gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.SCROLL_MASK)
    self.expose_handler = self.connect("expose-event", self.expose)
    self.click_handler = self.connect("button-press-event", self.button_click)
    self.release_handler = self.connect("button-release-event", self.button_release)
    self.motion_handler = self.connect("motion-notify-event", self.mouse_move)
    self.mouse_leave_handler = self.connect("leave-notify-event", self.mouse_leave)
    self.scroll_me_handler = self.connect("scroll-event", self.scroll_me)

    self.popup_win = None
    self.popup = None
    self.statusbar = statusbar

    self.codec = codec
    self.mytitle = mytitle
    self.graph = codec.graph(dump=False)
    self.startnode = None
    self.endnode = None

    self.changed_handler = HDA_SIGNAL.connect("hda-node-changed", self.hda_node_changed)

    ok = False
    for extra in [150, 200, 300]:
      if self.build(extra):
        ok = True
        break
    if not ok:
      print "Not all routes are placed correctly!!!"

  def __destroy(self, widget):
    if self.popup_win:
      self.popup_win.destroy()

  def __build(self, extra=50):
    self.nodes = []
    self.routes = []
    maxconns = 0
    for nid in self.codec.nodes:
      node = self.codec.nodes[nid]
      conns = max(self.codec.connections(nid, 0),
                  self.codec.connections(nid, 1))
      if conns > maxconns:
        maxconns = conns
    nodesize = max((maxconns * 5 + 10) * 2, 100)
    if self.graph:
      for y in range(len(self.graph)):
        for x in range(len(self.graph[0])):
          nid = self.graph[y][x]
          if not nid is None:
            node = self.codec.nodes[nid]
            w = Node(self.codec, node, x, y, nodesize, extra)
            self.nodes.append(w)
    sx = len(self.graph[0])*(nodesize+extra)+extra
    sy = len(self.graph)*(nodesize+extra)+extra
    self.set_size(sx, sy)
    total = 0
    for node in self.nodes:
      if not node.node.connections:
        continue
      for conn in node.node.connections:
        for node1 in self.nodes:
          if node1.node.nid == conn:
            total += 1
            break
    total *= 2
    total += 1
    position = 0
    for node in self.nodes:
      if not node.node.connections:
        continue
      for conn in node.node.connections:
        for node1 in self.nodes:
          if node1.node.nid == conn:
            r = Route(self.codec, node1, node, self.routes, self.nodes)
            self.routes.append(r)
            position += 1
            self.pdialog.set_fraction(float(position) / total)
            break
    res = True
    for route in self.routes:
      if not route.finish(self.routes, self.nodes):
        res = False
        break
      position += 1
      self.pdialog.set_fraction(float(position) / total)
    if not res:
      return
    # final step - optimize drawings
    while 1:
      size = self.compressx(sx)
      if not size:
        break
      sx -= size
    position += 1
    self.pdialog.set_fraction(float(position) / total)
    while 1:
      size = self.compressy(sy)
      if not size:
        break
      sy -= size
    self.set_size(sx, sy)
    return res

  def build(self, extra=50):
    self.pdialog = SimpleProgressDialog("Rendering routes")
    self.pdialog.show_all()
    res = self.__build(extra)
    self.pdialog.destroy()
    self.pdialog = None
    return res

  def expose(self, widget, event):
    if not self.flags() & gtk.REALIZED:
      return

    # background
    cr = self.bin_window.cairo_create()
    cr.set_source_rgb(1.0, 1.0, 1.0)
    cr.rectangle(event.area.x, event.area.y,
                 event.area.width, event.area.height)
    cr.clip()
    cr.paint()

    # draw nodes
    for node in self.nodes:
      node.expose(cr, event, self)
      
    # draw routes
    for route in self.routes:
      route.expose(cr, event)

  def compressx(self, sx):
    first = None
    for a in range(15, sx, 5):
      found = False
      for node in self.nodes:
        if node.has_x(a):
          found = True
          break
      if not found:
        for route in self.routes:
          if route.has_x(a):
            found = True
            break
      if not found:
        if first is None:
          first = a
        last = a
      elif first is not None:
        size = (last - first) + 5
        for node in self.nodes:
          node.compressx(first, size)
        for route in self.routes:
          route.compressx(first, size)
        return size
    return None

  def compressy(self, sy):
    first = None
    for a in range(15, sy, 5):
      found = False
      for node in self.nodes:
        if node.has_y(a):
          found = True
          break
      if not found:
        for route in self.routes:
          if route.has_y(a):
            found = True
            break
      if not found:
        if first is None:
          first = a
        last = a
      elif first is not None:
        size = (last - first) + 5
        for node in self.nodes:
          node.compressy(first, size)
        for route in self.routes:
          route.compressy(first, size)
        return size
    return None

  def hda_node_changed(self, obj, widget, node):
    if widget != self:
      self.queue_draw()

  def find_node(self, event):
    for node in self.nodes:
      what = node.in_area(event.x, event.y)
      if not what is None:
        return (node, what)
    return (None, None)
    
  def find_route(self, event):
    for route in self.routes:
      if route.in_area(event.x, event.y):
        return route

  def show_popup(self, event):
    screen_width = gtk.gdk.screen_width()
    screen_height = gtk.gdk.screen_height()

    if self.popup_win:
      self.popup_win.destroy()
    self.popup_win = gtk.Window(gtk.WINDOW_POPUP)
    label = gtk.Label()
    label.modify_font(get_fixed_font())
    label.set_text(self.popup)
    self.popup_win.add(label)
    self.popup_win.move(screen_width + 10, screen_height + 10)
    self.popup_win.show_all()
    popup_width, popup_height = self.popup_win.get_size()

    #rootwin = self.get_screen().get_root_window()
    #x, y, mods = rootwin.get_pointer()

    pos_x = screen_width - popup_width
    if pos_x < 0:
      pos_x = 0
    pos_y = screen_height - popup_height
    if pos_y < 0:
      pox_y = 0

    self.popup_win.move(int(pos_x), int(pos_y))
    #self.popup_win.show_all()

  def mouse_move(self, widget, event):
    oldpopup = self.popup
    self.popup = None
    redraw = False
    found = False
    for route in self.routes:
      if route.highlight:
        redraw = True
        route.highlight = False
    for node in self.nodes:
      if node.mouse_move(event.x, event.y, self):
        self.statusbar.pop(1)
        self.statusbar.push(1, node.longdesc())
        found = redraw = True
        break
    if not found:
      for route in self.routes:
        if route.mouse_move(event.x, event.y, self):
          self.statusbar.pop(1)
          self.statusbar.push(1, route.statusdesc())
          found = redraw = True
          break
    if not found:
      self.statusbar.pop(1)
    if redraw:
      self.queue_draw()
    if self.popup:
      if oldpopup != self.popup:
        self.show_popup(event)
    else:
      if self.popup_win:
        self.popup_win.destroy()
        self.popup_win = None

  def mouse_leave(self, widget, data=None):
    for route in self.routes:
      if route.highlight:
        redraw = True
        route.highlight = False
    if self.popup_win:
      self.popup_win.destroy()
      self.popup_win = None

  def mark_it(self, widget, node, what, enable):
    if what == "start":
      if enable:
        if not self.startnode:
          self.startnode = node
          self.queue_draw()
      else:
        if self.startnode:
          self.startnode = None
          self.queue_draw()
    elif what == "end":
      if enable:
        if not self.endnode:
          self.endnode = node
          self.queue_draw()
      else:
        if self.endnode:
          self.endnode = None
          self.queue_draw()

  def mark_route(self, widget, route, what, enable):
    if what == "mark":
      if enable:
        if not route.marked:
          route.marked = enable
          self.queue_draw()
      else:
        if route.marked:
          route.marked = False
          self.queue_draw()

  def node_win_destroy(self, widget, node):
    TRACKER.close(node.win)
    node.win = None

  def open_node(self, widget, node):
    if self.popup_win:
      self.popup_win.destroy()
    if not node.win:
      win = gtk.Window()
      win.set_default_size(500, 600)
      gui = NodeGui(node=node.node)
      win.set_title(self.mytitle + ' ' + gui.mytitle)
      win.add(gui)
      win.connect("destroy", self.node_win_destroy, node)
      win.show_all()
      node.win = win
      TRACKER.add(win)
    else:
      node.win.present()
    
  def button_click(self, widget, event):
    if event.button != 3:
      if event.button == 8:
        self.scroll_me(self, DummyScrollEvent(gtk.gdk.SCROLL_LEFT))
      elif event.button == 9:
        self.scroll_me(self, DummyScrollEvent(gtk.gdk.SCROLL_RIGHT))
      return False
    node, what = self.find_node(event)
    m = None
    if node:
      m = gtk.Menu()
      i = gtk.MenuItem("Open")
      i.connect("activate", self.open_node, node)
      i.show()
      m.append(i)
      if what in ["src", "dst"]:
        routes1 = node.src_routes
        text = "Mark Route From"
        if what == "dst":
          routes1 = node.dst_routes
          text = "Mark Route To"
        routes = []
        for route in routes1:
          if not route.marked:
            routes.append(route)
        if routes:
          i = None
          if len(routes) == 1:
            i = gtk.MenuItem(text + ' ' + routes[0].longdesc())
            i.connect("activate", self.mark_route, routes[0], "mark", True)
          else:
            menu = gtk.Menu()
            for route in routes:
              i = gtk.MenuItem(route.longdesc())
              i.connect("activate", self.mark_route, route, "mark", True)
              i.show()
              menu.append(i)
            i = gtk.MenuItem(text)
            i.set_submenu(menu)
          if i:
            i.show()
            m.append(i)
      if what in ["src", "dst"]:
        routes1 = node.src_routes
        text = "Unmark Route From"
        if what == "dst":
          routes1 = node.dst_routes
          text = "Unmark Route To"
        routes = []
        for route in routes1:
          if route.marked:
            routes.append(route)
        if routes:
          i = None
          if len(routes) == 1:
            i = gtk.MenuItem(text + ' ' + routes[0].longdesc())
            i.connect("activate", self.mark_route, routes[0], "mark", False)
          else:
            menu = gtk.Menu()
            for route in routes:
              i = gtk.MenuItem(route.longdesc())
              i.connect("activate", self.mark_route, route, "mark", False)
              i.show()
              menu.append(i)
            i = gtk.MenuItem(text)
            i.set_submenu(menu)
          if i:
            i.show()
            m.append(i)
      if not self.startnode:
        i = gtk.MenuItem("Mark as start point")
        i.connect("activate", self.mark_it, node, "start", True)
      else:
        i = gtk.MenuItem("Clear start point")
        i.connect("activate", self.mark_it, None, "start", False)
      i.show()
      m.append(i)
      if not self.endnode:
        i = gtk.MenuItem("Mark as finish point")
        i.connect("activate", self.mark_it, node, "end", True)
      else:
        i = gtk.MenuItem("Clear finish point")
        i.connect("activate", self.mark_it, None, "end", False)
      i.show()
      m.append(i)
    else:
      route = self.find_route(event)
      if route:
        m = gtk.Menu()
        if not route.marked:
          i = gtk.MenuItem("Mark selected route %s" % route.shortdesc())
          i.connect("activate", self.mark_route, route, "mark", True)
        else:
          i = gtk.MenuItem("Clear selected route %s" % route.shortdesc())
          i.connect("activate", self.mark_route, route, "mark", False)
        i.show()
        m.append(i)
    if m:
      m.popup(None, None, None, event.button, event.time, None)
    return False 
    
  def button_release(self, widget, event):
    pass

  def scroll_me(self, widget, event):
    if event.direction == gtk.gdk.SCROLL_UP:
      adj = self.get_vadjustment()
      adj.set_value(adj.get_value()-40)
    elif event.direction == gtk.gdk.SCROLL_DOWN:
      adj = self.get_vadjustment()
      adj.set_value(adj.get_value()+40)
    elif event.direction == gtk.gdk.SCROLL_LEFT:
      adj = self.get_hadjustment()
      adj.set_value(adj.get_value()-40)
    elif event.direction == gtk.gdk.SCROLL_RIGHT:
      adj = self.get_hadjustment()
      adj.set_value(adj.get_value()+40)

gobject.type_register(CodecGraphLayout)

class CodecGraph(gtk.Window):

  def __init__(self, codec):
    gtk.Window.__init__(self)
    self.codec = codec
    self.connect('destroy', self.__destroy)
    self.set_default_size(800, 600)
    self.set_title(self.__class__.__name__ + ' ' + self.codec.name)
    self.set_border_width(0)

    table = gtk.Table(2, 3, False)
    self.add(table)

    statusbar = gtk.Statusbar()
    self.layout = CodecGraphLayout(None, None, codec, self.get_title(), statusbar)
    table.attach(self.layout, 0, 1, 0, 1, gtk.FILL|gtk.EXPAND,
                 gtk.FILL|gtk.EXPAND, 0, 0)
    vScrollbar = gtk.VScrollbar(None)
    table.attach(vScrollbar, 1, 2, 0, 1, gtk.FILL|gtk.SHRINK,
                 gtk.FILL|gtk.SHRINK, 0, 0)
    hScrollbar = gtk.HScrollbar(None)
    table.attach(hScrollbar, 0, 1, 1, 2, gtk.FILL|gtk.SHRINK,
                 gtk.FILL|gtk.SHRINK, 0, 0)	
    vAdjust = self.layout.get_vadjustment()
    vScrollbar.set_adjustment(vAdjust)
    hAdjust = self.layout.get_hadjustment()
    hScrollbar.set_adjustment(hAdjust)
    table.attach(statusbar, 0, 2, 2, 3, gtk.FILL|gtk.SHRINK,
                 gtk.FILL|gtk.SHRINK, 0, 0)
    self.show_all()
    GRAPH_WINDOWS[codec] = self
    TRACKER.add(self)

  def __destroy(self, widget):
    del GRAPH_WINDOWS[self.codec]
    TRACKER.close(self)

def create_graph(codec):
  if codec in GRAPH_WINDOWS:
    GRAPH_WINDOWS[codec].present()
  else:
    CodecGraph(codec)
