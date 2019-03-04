#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import os
import sys

from os.path import join, dirname

import json
import simplejson

from collections import OrderedDict

false = False

curdir = dirname(__file__)

Dashboard_Widget_Source_Code = OrderedDict(
# On your target dashboard, click "Actions", "View/edit source", then ...
# ... copy entire source code from "Dashboard source" window and paste here.

)

CW_Remote_Ini = OrderedDict()

# Can be either "paged" or "duplex"
CW_Remote_layout = "paged"

# Set these values from AWS/IAM/Users "cloudwatch_widget_keyhole" which has been granted ...
# ... "cloudwatch_widget_keyhole_policy".
# This policy has been created with only "Read", "GetMetricWidgetImage" permission, ...
# ... the minimum permissions to monitor dashboard widgets, and no other access permissions.
CW_Remote_aws_access_id = "xxx"
CW_Remote_aws_secret_key = "xxx"

Target_TimeZone = "-0500" # This is New York City, CW_Remote will choose standard or daylight as appropriate

Target_Device_Horizontal_Resolution = 1280
Target_Device_Vertical_Resolution = 800

widget_descriptor_base = \
{
    "start": "-PT24H",
    "timezone": "-0500",
    "width": 1280,
    "height": 380,
}

def Initialize_Widget_Descriptor ( this_widget_descriptor ):
    widget_properties = this_widget_descriptor.get("properties", {})
    for key, value in widget_descriptor_base.items():
        widget_properties[key] = value
    return widget_properties

def main ( ):
    CW_Remote_Ini["layout"] = CW_Remote_layout
    CW_Remote_Ini["aws_access_id"] = CW_Remote_aws_access_id
    CW_Remote_Ini["aws_secret_key"] = CW_Remote_aws_secret_key

    widget_descriptor_list = Dashboard_Widget_Source_Code.get("widgets", [])

    widget_descriptor_base["timezone"] = Target_TimeZone

    widget_descriptor_base["width"] = Target_Device_Horizontal_Resolution
    widget_descriptor_base["height"] = int(round((Target_Device_Vertical_Resolution * 0.9) / 2)) + 20

    if (len(widget_descriptor_list) > 0):
        upper_widget_descriptor = widget_descriptor_list[0]
        widget_properties = upper_widget_descriptor.get("properties", {})
        CW_Remote_Ini["region_name"] = widget_properties.get("region", "xxx")
        CW_Remote_Ini["upper_widget_descriptor"] = Initialize_Widget_Descriptor(upper_widget_descriptor)

    if (len(widget_descriptor_list) > 1):
        lower_widget_descriptor = widget_descriptor_list[1]
        CW_Remote_Ini["lower_widget_descriptor"] = Initialize_Widget_Descriptor(lower_widget_descriptor)

    with open(join(curdir, "test_CW_Remote.ini"), "w") as cw_remote_ini_file:
        cw_remote_ini_file.write(simplejson.dumps(CW_Remote_Ini, indent=2))

if __name__ == '__main__':
    status_value = main()
    sys.exit(status_value)
