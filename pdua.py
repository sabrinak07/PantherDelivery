# Sabrina Kessler
# CSC 450 - PantherDelivery Project
# Description: User command-line client for registering packages, checking status, and canceling deliveries.

#!/usr/bin/env python3

import argparse
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"


def print_json(data):
    print(json.dumps(data, indent=4))


def api_request(method, path, body=None):
    url = BASE_URL + path

    data = None
    headers = {}

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")

            if response_body:
                return json.loads(response_body)

            return {}

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")

        print(f"Error {error.code}:")

        if error_body:
            try:
                print_json(json.loads(error_body))
            except json.JSONDecodeError:
                print(error_body)

        return None

    except urllib.error.URLError:
        print("Could not connect to the PantherDelivery API.")
        print("Make sure app.py is running first.")
        return None


def register_package(args):
    package_data = {
        "sender": args.sender,
        "pickup_loc": args.pickup,
        "recipient": args.recipient,
        "delivery_loc": args.delivery
    }

    result = api_request("POST", "/v1/packages", package_data)

    if result:
        print("Package registered:")
        print_json(result)


def check_status(args):
    result = api_request("GET", f"/v1/deliveries/{args.id}")

    if result:
        print("Delivery status:")
        print_json(result)


def cancel_delivery(args):
    result = api_request("PUT", f"/v1/deliveries/{args.id}", {
        "status": "CANCELLED"
    })

    if result:
        print("Cancel request result:")
        print_json(result)


def main():
    parser = argparse.ArgumentParser(description="PantherDelivery User Agent")
    subparsers = parser.add_subparsers(dest="command")

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--sender", required=True)
    register_parser.add_argument("--pickup", required=True)
    register_parser.add_argument("--recipient", required=True)
    register_parser.add_argument("--delivery", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--id", required=True)

    cancel_parser = subparsers.add_parser("cancel")
    cancel_parser.add_argument("--id", required=True)

    args = parser.parse_args()

    if args.command == "register":
        register_package(args)
    elif args.command == "status":
        check_status(args)
    elif args.command == "cancel":
        cancel_delivery(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()