from ping3 import ping
from models.device import Device, db


def check_device(ip):
    try:
        response = ping(ip, timeout=2)

        if response is None:
            return "Offline"

        return "Online"

    except Exception:
        return "Offline"


def scan_all_devices():

    devices = Device.query.all()

    for device in devices:
        device.status = check_device(device.ip_address)

    db.session.commit()

    print("Network Scan Completed")