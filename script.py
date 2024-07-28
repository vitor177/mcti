        #!/usr/bin/python3

# Example client for the AmmonitOR REST API
# Copyright 2017 Ammonit Measurement GmbH

import argparse
import json
import sys

import requests

device_serial = "D230012"
server_url = "https://or.ammonit.com"  # URL do servidor AmmonitOR
project_key = "GWFR"  # Project Key
token = "f7c9d9394c73b9bd3d020eb485d5387de6b4d31b"  # Token de autenticação

def get_options():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-a",
        "--app",
        help="Provide the application name",
        default="Ammonit API example client",
    )
    parser.add_argument("-d", "--device", help="Device serial, e.g. 'D123456'")
    parser.add_argument(
        "-D",
        "--date",
        help="Specify date to get completeness " "e.g. 2017-01-01T00:00:00",
    )
    parser.add_argument("-e", "--export", help="Export ID e.g. 123")
    parser.add_argument(
        "-f",
        "--file",
        help="Device original filename, " "e.g. 'D123456_20160808.csv'",
    )
    parser.add_argument(
        "-F",
        "--date_from",
        help="Specify date from, " "e.g. 2017-01-01T00:00:00",
    )
    parser.add_argument(
        "-i",
        "--filetype",
        help="\n".join(["Specify the type of file:"] + FILE_TYPES),
    )
    parser.add_argument(
        "-p",
        "--project",
        help="AmmonitOR project key, e.g. 'ABCD'",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--server-url",
        help="Server URL to use, e.g. https://or.ammonit.com",
        default="https://or.ammonit.com",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="Token to communicate with AmmonitOR, "
        "coming from requesting the permission view",
    )
    parser.add_argument(
        "-T", "--date_to", help="Specify date to, " ".e.g. 2017-12-31T00:00:00"
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Valid AmmonitOR user, e.g. bach@example.com",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--view",
        help="\n".join(
            ["Avaliable views:"]
            + sorted(
                [
                    "%-12s - %s" % (k, v.__doc__ or "(undocumented)")
                    for k, v in REQUESTABLES.items()
                ]
            )
        ),
        required=True,
    )
    return parser.parse_args()


def format_output(output):
    return json.dumps(json.loads(output.decode("utf-8")), indent=4, sort_keys=True)


def get_token(options, header):
    "make a enquiry for a new app in AmmonitOR"
    url = options.server_url + "/api/auth-token/"
    data = {
        "username": options.username,
        "project_key": options.project,
        "app_id": options.app,
    }
    r = requests.post(url, data)
    print(format_output(r.content))


def list_devices(options, header):
    "list AmmonitOR devices in project"
    if options.project:
        url = options.server_url + "/api/%s/loggers-list/" % (options.project)
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print("Please provide the project key!")


def get_device_data(options, header):
    "get the device metadata"
    if options.project and options.device:
        url = options.server_url + "/api/%s/%s/" % (
            options.project,
            options.device,
        )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print("Please provide the project key and device serial!")


def list_files(options, header):
    "list data files for a device"
    if options.project and options.device and options.filetype:
        url = options.server_url + "/api/%s/%s/files/%s/" % (
            options.project,
            options.device,
            options.filetype,
        )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print("Please provide the project key and device serial!")


def get_download(options, header):
    "download data files of given project and device"
    if options.project and options.device and options.file and options.filetype:
        url = options.server_url + "/api/%s/%s/files/%s/%s/" % (
            options.project,
            options.device,
            options.filetype,
            options.file,
        )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print(
            "Please provide the project key, device serial, "
            " and name of file to be downloaded!"
        )


def list_exports(options, header):
    if options.project and options.device:
        url = options.server_url + "/api/%s/%s/export-list/" % (
            options.project,
            options.device,
        )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print("Please provide the project key and device serial!")


def get_export_download(options, header):
    if options.project and options.device and options.export and options.date_from:
        url = options.server_url + "/api/%s/%s/export/%s/?date_from=%s&date_to=%s" % (
            options.project,
            options.device,
            options.export,
            options.date_from,
            options.date_to,
        )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print(
            "Please provide the project key, device serial, export id and" " date from!"
        )


def get_completeness_values(options, header):
    if options.project and options.device:
        if options.date_from and options.date_to:
            url = (
                options.server_url
                + "/api/%s/%s/completeness/?date_from=%s&date_to=%s"
                % (
                    options.project,
                    options.device,
                    options.date_from,
                    options.date_to,
                )
            )
        else:
            url = options.server_url + "/api/%s/%s/completeness/" % (
                options.project,
                options.device,
            )
        r = requests.get(url, headers=header)
        print(format_output(r.content))
    else:
        print(
            "Please provide the project key, device serial and optionally"
            " both date from and date_to!"
        )


def get_completeness_day(options, header):
    if options.project and options.device:
        if options.date:
            url = options.server_url + "/api/%s/%s/completeness/day/?date=%s" % (
                options.project,
                options.device,
                options.date,
            )
            r = requests.get(url, headers=header)
            print(format_output(r.content))
        else:
            print("Please provide the date!")
    else:
        print("Please provide the project key and device serial")


def get_connections(options, header):
    if options.project and options.device:
        if options.date_from and options.date_to:
            url = (
                options.server_url
                + "/api/%s/%s/connections/?date_from=%s&date_to=%s"
                % (
                    options.project,
                    options.device,
                    options.date_from,
                    options.date_to,
                )
            )
            r = requests.get(url, headers=header)
            print(format_output(r.content))
        else:
            print("Please provide the date from and to!")
    else:
        print("Please provide the project key and device serial")


REQUESTABLES = {
    "device": get_device_data,
    "download": get_download,
    "export_file": get_export_download,
    "exports": list_exports,
    "files": list_files,
    "devices": list_devices,
    "permission": get_token,
    "completeness": get_completeness_values,
    "day_completeness": get_completeness_day,
}


FILE_TYPES = ["primary", "secondary", "tertiary", "config", "gust", "logbook"]


if __name__ == "__main__":
    options = get_options()

    header = None

    if options.view != "permission":
        if options.token:
            header = {"Authorization": "Token " + options.token}
        else:
            print("Please provide the token for authentication!")
            sys.exit(1)

    if options.view in REQUESTABLES.keys():
        REQUESTABLES[options.view](options, header)
    else:
        print("Unknow view '%s'" % options.view)
        print("Use one of " + ", ".join(sorted(REQUESTABLES.keys())))

      