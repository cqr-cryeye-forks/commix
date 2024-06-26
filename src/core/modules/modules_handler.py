#!/usr/bin/env python
# encoding: UTF-8

"""
This file is part of Commix Project (https://commixproject.com).
Copyright (c) 2014-2021 Anastasios Stasinopoulos (@ancst).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
For more see the file 'readme/COPYING' for copying permission.
"""

from src.utils import menu
from src.utils import settings

"""
Load modules
"""


def load_modules(url, http_request_method, filename):
    # Check if defined the ICMP exfiltration module
    if menu.options.ip_icmp_data:
        try:
            # The ICMP exfiltration module
            from src.core.modules.icmp_exfiltration import icmp_exfiltration
            # The ICMP exfiltration handler
            icmp_exfiltration.icmp_exfiltration_handler(url, http_request_method)
        except ImportError as err_msg:
            print("\n" + settings.print_critical_msg(err_msg))
            raise SystemExit()
        raise SystemExit()

    # Check if defined the DNS exfiltration module
    if menu.options.dns_server:
        try:
            # The DNS exfiltration module
            from src.core.modules.dns_exfiltration import dns_exfiltration
            # The DNS exfiltration handler
            dns_exfiltration.dns_exfiltration_handler(url, http_request_method)
        except ImportError as err_msg:
            print("\n" + settings.print_critical_msg(err_msg))
            raise SystemExit()
        raise SystemExit()

    # Check if defined the shellshock module
    if menu.options.shellshock:
        try:
            # The shellshock module
            from src.core.modules.shellshock import shellshock
            # The shellshock handler
            shellshock.shellshock_handler(url, http_request_method, filename)
        except ImportError as err_msg:
            print("\n" + settings.print_critical_msg(err_msg))
            raise SystemExit()
        raise SystemExit()
