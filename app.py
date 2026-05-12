# Sabrina Kessler
# CSC 450 - PantherDelivery Project
# Description: Flask API server for the PantherDelivery campus logistics system.

from flask import Flask, request, jsonify
import json
import threading
from datetime import datetime

app = Flask(__name__)

data_lock = threading.Lock()

PACKAGES_FILE = "packages.json"
ROBOTS_FILE = "robots.json"
DELIVERIES_FILE = "deliveries.json"


def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def make_id(prefix, items):
    return f"{prefix}_{len(items) + 1:03d}"


def now():
    return datetime.now().isoformat()


# Package Endpoints

''' --------- Register a new package for pickup and delivery ---------'''

@app.route("/v1/packages", methods=["POST"])
def register_package():
    data = request.json

    if not data:
        return jsonify({"error": "No JSON sent"}), 400

    with data_lock:
        packages = load_json(PACKAGES_FILE)

        package = {
            "id": make_id("pkg", packages),
            "sender": data.get("sender"),
            "pickup_loc": data.get("pickup_loc"),
            "recipient": data.get("recipient"),
            "delivery_loc": data.get("delivery_loc"),
            "status": "REGISTERED"
        }

        packages.append(package)
        save_json(PACKAGES_FILE, packages)

    return jsonify(package), 201

''' --------- Get all registered packages waiting to be assigned --------- '''

@app.route("/v1/packages", methods=["GET"])
def get_packages():
    status = request.args.get("status")
    packages = load_json(PACKAGES_FILE)

    if status:
        packages = [p for p in packages if p["status"] == status]

    return jsonify({"packages": packages}), 200


# Robot Endpoints

''' --------- Get available robots ---------'''

@app.route("/v1/robots", methods=["GET"])
def get_robots():
    status = request.args.get("status")
    robots = load_json(ROBOTS_FILE)

    if status:
        robots = [r for r in robots if r["status"] == status]

    return jsonify({"robots": robots}), 200


# Delivery Endpoints

''' --------- Create a new delivery by assigning a package to a robot ---------'''

@app.route("/v1/deliveries", methods=["POST"])
def create_delivery():
    data = request.json

    if not data:
        return jsonify({"error": "No JSON sent"}), 400

    package_id = data.get("package_id")
    robot_id = data.get("robot_id")

    with data_lock:
        packages = load_json(PACKAGES_FILE)
        robots = load_json(ROBOTS_FILE)
        deliveries = load_json(DELIVERIES_FILE)

        package = next((p for p in packages if p["id"] == package_id), None)
        robot = next((r for r in robots if r["id"] == robot_id), None)

        if package is None:
            return jsonify({"error": "Package not found"}), 404

        if robot is None:
            return jsonify({"error": "Robot not found"}), 404

        if package["status"] != "REGISTERED":
            return jsonify({"error": "Package is not available"}), 400

        if robot["status"] != "AVAILABLE":
            return jsonify({"error": "Robot is not available"}), 400

        delivery = {
            "id": make_id("del", deliveries),
            "package_id": package_id,
            "robot_id": robot_id,
            "status": "PENDING_PICKUP",
            "created_at": now(),
            "last_updated": now(),
            "pickup_time": None,
            "delivery_time": None
        }

        package["status"] = "ASSIGNED"
        robot["status"] = "BUSY"

        deliveries.append(delivery)

        save_json(PACKAGES_FILE, packages)
        save_json(ROBOTS_FILE, robots)
        save_json(DELIVERIES_FILE, deliveries)

    return jsonify(delivery), 201

''' --------- List all active deliveries --------- '''

@app.route("/v1/deliveries", methods=["GET"])
def get_active_deliveries():
    deliveries = load_json(DELIVERIES_FILE)
    packages = load_json(PACKAGES_FILE)

    active_deliveries = []

    for delivery in deliveries:
        if delivery["status"] not in ["DELIVERED", "CANCELLED"]:
            package = next((p for p in packages if p["id"] == delivery["package_id"]), None)

            active_deliveries.append({
                "id": delivery["id"],
                "robot_id": delivery["robot_id"],
                "package_id": delivery["package_id"],
                "pickup_time": delivery["pickup_time"],
                "sender": package["sender"] if package else None,
                "recipient": package["recipient"] if package else None,
                "status": delivery["status"]
            })

    return jsonify({"deliveries": active_deliveries}), 200

''' --------- Check the status of a delivery ---------'''

@app.route("/v1/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    deliveries = load_json(DELIVERIES_FILE)

    delivery = next((d for d in deliveries if d["id"] == delivery_id), None)

    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404

    return jsonify(delivery), 200


''' --------- Update the status of a delivery (e.g., mark as IN_TRANSIT, DELIVERED, or CANCELLED) ---------'''
@app.route("/v1/deliveries/<delivery_id>", methods=["PUT"])
def update_delivery(delivery_id):
    data = request.json

    if not data:
        return jsonify({"error": "No JSON sent"}), 400

    new_status = data.get("status")
    
    allowed_statuses = ["PENDING_PICKUP", "IN_TRANSIT", "DELIVERED", "CANCELLED"]

    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid status"}), 400
    
    with data_lock:
        deliveries = load_json(DELIVERIES_FILE)
        robots = load_json(ROBOTS_FILE)

        delivery = next((d for d in deliveries if d["id"] == delivery_id), None)

        if delivery is None:
            return jsonify({"error": "Delivery not found"}), 404

        if new_status == "CANCELLED" and delivery["status"] in ["IN_TRANSIT", "DELIVERED"]:
            return jsonify({"error": "Delivery cannot be cancelled after pickup"}), 400

        delivery["status"] = new_status
        delivery["last_updated"] = now()

        if new_status == "IN_TRANSIT":
            delivery["pickup_time"] = now()

        if new_status == "DELIVERED":
            delivery["delivery_time"] = now()

            robot = next((r for r in robots if r["id"] == delivery["robot_id"]), None)
            if robot:
                robot["status"] = "AVAILABLE"

            save_json(ROBOTS_FILE, robots)

        if new_status == "CANCELLED":
            robot = next((r for r in robots if r["id"] == delivery["robot_id"]), None)
            if robot:
                robot["status"] = "AVAILABLE"

            save_json(ROBOTS_FILE, robots)

        save_json(DELIVERIES_FILE, deliveries)

    return jsonify(delivery), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)