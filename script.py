#!/usr/bin/python
# Trigger Profilematic rule by BT connected/disconnected
# author: slarti

import dbus, gobject

# Set up profilematic interface and get a list of rule names:
sesbus = dbus.SessionBus()
pm_obj = sesbus.get_object('org.ajalkane.profilematic', '/org/ajalkane/profilematic')
pm_intf = dbus.Interface(pm_obj, 'org.ajalkane.profilematic')
rulenames = pm_intf.getRuleNames()

# Set up some functions to use when handling the dbus event:
def menu(list, question):
        print (30 * '-')
        print ("Pick one from these:")
        for entry in list:
                print "  ",1 + list.index(entry),
                print ") " + entry
        print (30 * '-')

        return list[(int(raw_input(question)) - 1)]

def get_disconnected_rule():
        rule_list = ["No action"] + rulenames
        disconnected_rule = menu(rule_list, "Pick the rule whose actions you want to execute when device is disconnected: ")
        print "The actions of (%s) will be executed on device disconnect" %disconnected_rule

        return disconnected_rule

def get_connected_rule():
        rule_list = ["No action"] + rulenames
        connected_rule = menu(rule_list, "Pick the rule whose actions you want to execute when device is connected: ")
        print "The actions of (%s) will be executed on device connect" %connected_rule

        return connected_rule

def trigger_action(rulename):
        if rulename == 0:
                print "No action wanted."
        else:
                pm_intf.executeActionsByRuleName(rulename)
                print rulename, "executed."

# Set up loop to listen for dbus signal:
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


# Get the BT adapter path and link device names to device paths in a dict:
bus = dbus.SystemBus()
bluez = bus.get_object('org.bluez', '/')
adapter_path = bluez.ListAdapters(dbus_interface='org.bluez.Manager')[0]
adapter = bus.get_object('org.bluez', adapter_path)
devices = adapter.ListDevices(dbus_interface='org.bluez.Adapter')
device_dict = {}

for device_path in devices:
        deviceprops = bus.get_object('org.bluez', device_path).GetProperties(dbus_interface='org.bluez.Device')
        device_dict.update({deviceprops ['Alias']:device_path})

# Get device, connect rule and disconnect rule from user:
# TODO: Maybe get these from a config file or arguments?
device = menu(device_dict.keys(),"The name of the device to follow: ")
device_path = device_dict [device]
print "Now following the device: ",device, "in path: ",device_path

connected_rule = get_connected_rule()
if connected_rule == "No action":
        device_connected = 0
else:
        device_connected = connected_rule

disconnected_rule = get_disconnected_rule()
if disconnected_rule == "No action":
        device_disconnected = 0
else:
        device_disconnected = disconnected_rule


# Handle dbus signal:
def process_signal(property, message):
        if message == 0:
                print device, "disconnected. Triggering action."
                trigger_action(device_disconnected)
        else:
                print device, "connected. Triggering action."
                trigger_action(device_connected)

# Add signal receiver:
bus.add_signal_receiver(process_signal,path=device_path,dbus_interface='org.bluez.Device',signal_name='PropertyChanged')

loop = gobject.MainLoop()
loop.run()
