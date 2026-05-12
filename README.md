# PantherDelivery – Campus Logistics REST API

PantherDelivery is a small campus delivery management system built for CSC 450 Computer Networks. It simulates how an autonomous robot delivery service could register packages, assign available robots, and track delivery progress across campus.

The project includes a Flask REST API server plus two command-line clients: one for users and one for robot agents.

## What the project does

- Registers packages for campus pickup and delivery
- Lists packages waiting to be assigned
- Lists available delivery robots
- Assigns a robot to a package and creates a delivery
- Tracks delivery status updates such as `PENDING_PICKUP`, `IN_TRANSIT`, `DELIVERED`, and `CANCELLED`
- Prevents deliveries from being cancelled after pickup
- Stores package, robot, and delivery data in local JSON files
- Uses a thread lock when updating shared JSON data

## Tech used

- Python 3
- Flask
- JSON file storage
- `argparse` for command-line clients
- `urllib.request` for client API calls
- `threading.Lock` for basic thread safety

## Project structure

```text
PantherDelivery/
├── app.py              # Flask REST API server
├── pdua.py             # PantherDelivery User Agent
├── pdra.py             # PantherDelivery Robot Agent
├── packages.json       # Package data
├── robots.json         # Robot data
├── deliveries.json     # Delivery data
└── README.md
```

## REST API overview

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/v1/packages` | Register a new package |
| `GET` | `/v1/packages?status=REGISTERED` | View unassigned packages |
| `GET` | `/v1/robots?status=AVAILABLE` | View available robots |
| `POST` | `/v1/deliveries` | Assign a robot to a package |
| `GET` | `/v1/deliveries` | List active deliveries |
| `GET` | `/v1/deliveries/<delivery_id>` | Check one delivery status |
| `PUT` | `/v1/deliveries/<delivery_id>` | Update or cancel a delivery |

## How to run

First, install Flask if needed:

```bash
pip3 install flask
```

Then start the API server:

```bash
python3 app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

Keep this terminal window open while testing the clients.

## User Agent examples

Register a package:

```bash
python3 pdua.py register --sender "Sabrina" --pickup "SCB 414" --recipient "Pres Storm" --delivery "LEV 100"
```

Check a delivery status:

```bash
python3 pdua.py status --id del_001
```

Cancel a delivery before pickup:

```bash
python3 pdua.py cancel --id del_001
```

## Robot Agent examples

Poll for packages waiting to be assigned:

```bash
python3 pdra.py --poll-pickup
```

Poll for available robots:

```bash
python3 pdra.py --poll-robots
```

Assign a robot to a package:

```bash
python3 pdra.py --assign --robot robot_001 --package pkg_001
```

Update delivery status:

```bash
python3 pdra.py --update-status --delivery del_001 --status IN_TRANSIT
```

List active deliveries:

```bash
python3 pdra.py --list-active
```

## Design notes

This project follows a REST-style design with versioned `/v1` endpoints, JSON request and response bodies, and standard HTTP response codes. The API is stateless from the client side, so each request includes the information needed for the server to process it.

Because multiple clients could try to assign the same package or robot at the same time, the server uses a `threading.Lock` around write operations to reduce race-condition issues with the JSON files.

## Current limitations

This is a class project, so it intentionally keeps the storage simple. The API uses JSON files instead of a full database and does not include authentication, authorization, or a web front end.
