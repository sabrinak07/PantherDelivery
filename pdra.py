# Sabrina Kessler
# CSC 450 - PantherDelivery Project
# Description: Robot command-line client for polling packages/robots, assigning deliveries, and updating delivery status.

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


def poll_pickup():
    result = api_request("GET", "/v1/packages?status=REGISTERED")

    if result:
        print("Unassigned packages:")
        print_json(result)


def poll_robots():
    result = api_request("GET", "/v1/robots?status=AVAILABLE")

    if result:
        print("Available robots:")
        print_json(result)


def assign_delivery(args):
    delivery_data = {
        "package_id": args.package_id,
        "robot_id": args.robot
    }

    result = api_request("POST", "/v1/deliveries", delivery_data)

    if result:
        print("Delivery created:")
        print_json(result)


def update_status(args):
    result = api_request("PUT", f"/v1/deliveries/{args.delivery}", {
        "status": args.status
    })

    if result:
        print("Delivery updated:")
        print_json(result)


def list_active():
    result = api_request("GET", "/v1/deliveries")

    if result:
        print("Active deliveries:")
        print_json(result)


def main():
    parser = argparse.ArgumentParser(description="PantherDelivery Robot Agent")

    parser.add_argument("--poll-pickup", action="store_true")
    parser.add_argument("--poll-robots", action="store_true")
    parser.add_argument("--assign", action="store_true")
    parser.add_argument("--robot")
    parser.add_argument("--package", dest="package_id")
    parser.add_argument("--update-status", action="store_true")
    parser.add_argument("--delivery")
    parser.add_argument("--status")
    parser.add_argument("--list-active", action="store_true")

    args = parser.parse_args()

    if args.poll_pickup:
        poll_pickup()

    elif args.poll_robots:
        poll_robots()

    elif args.assign:
        if not args.robot or not args.package_id:
            print("Use: python3 pdra.py --assign --robot robot_001 --package pkg_001")
            return

        assign_delivery(args)

    elif args.update_status:
        if not args.delivery or not args.status:
            print("Use: python3 pdra.py --update-status --delivery del_001 --status IN_TRANSIT")
            return

        update_status(args)

    elif args.list_active:
        list_active()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()