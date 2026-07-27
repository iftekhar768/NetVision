from ping3 import ping


def check_device(ip):

    try:

        response = ping(ip, timeout=2)

        if response is None:
            return "Offline"

        return "Online"

    except Exception:
        return "Offline"