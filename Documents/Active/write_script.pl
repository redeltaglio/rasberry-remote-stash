#!/usr/bin/perl

# Copyright 2020 Harry Bloomberg hbloomb@gmail.com
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This program is designed to generate a shell script to redirect
#    PulseAudio sinks and sources to NoMachine for the remote operation
#    of an amateur radio station.  See documentation at
#    http://www.w1hkj.com/W3YJ

# Get list of sinks
$i=0;
foreach $_ (`pacmd list-sinks | grep -e 'index:' -e device.string -e 'name:'`) {
   chomp;
   next if (/^\s+index/);
   next if (/^\s+device/);
   next if (/^\s+\* index/);
   $_ =~ /^\s+name\: \<(.+)\>/;
   $sink[$i++] = $1;
}

# Get list of sources
$i=0;
foreach $_ (`pacmd list-sources| grep -e 'index:' -e device.string -e 'name:'`) {
   chomp;
   next if (/^\s+index/);
   next if (/^\s+device/);
   next if (/^\s+\* index/);
   #print "source $i=|$_\n";
   $_ =~ /^\s+name\: \<(.+)\>/;
   $source[$i++] = $1;
}

print "Available sources:\n";
$sources=0;
foreach(@source) {
   print "$sources: $source[$sources]\n";
   $sources++;
}

# Ask user to select a source for use in the script

print "Select a source >";
$source_to_use = <>;
chomp $source_to_use;
print "Source to use:$source[$source_to_use]\n";
print "\n";

print "Available sinks:\n";
$sinks=0;
foreach (@sink) {
   print "$sinks: $sink[$sinks]\n";
   $sinks++;
}

# Ask user to select a sink for use in the script

print "Select a sink >";
$sink_to_use = <>;
chomp $sink_to_use;
print "Sink to use:$sink[$sink_to_use]\n";
print "\n";
$script_source = $source[$source_to_use];
$script_sink = $sink[$sink_to_use];

# Generate the script and show to user

print "Script:\n";
$script = <<SCRIPT;
pacmd set-default-source $script_source
pactl load-module module-null-sink sink_name=dummy
pacmd set-default-sink dummy
pacmd load-module module-loopback source=$script_source sink=dummy
pactl load-module module-loopback source=nx_voice_out.monitor sink=$script_sink
pacmd unload-module module-suspend-on-idle
SCRIPT
print $script;

# Ask user if they want to save the script or overwrite an existing script.

print "Enter a file name for script >";
$filename = <>;
chomp $filename;
if (-e $filename) {
   print "File $filename exists.  Replace? (Y or y to replace) >";
   $answer = <>;
   chomp $answer;
   print "answer = $answer\n";
   unless ($answer eq 'Y' || $answer eq 'y') {
      print "File $filename not written.  Done.\n";
      exit;
   }
}
open (SCRIPT, ">$filename") || die "Unable to open $filename for writing.\n"; 
print SCRIPT $script;
close (SCRIPT);
`chmod u+x $filename`;
print "Script $filename written.\n";

