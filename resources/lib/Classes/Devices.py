from datetime import datetime, timedelta

from resources.lib.Utils import Utils


class Device(object):
    def __init__(self, customer_defined_name="", device_class="",
                 device_id="", device_name="", device_status="", registered=0):
        self.customer_defined_name = customer_defined_name
        self.device_class = device_class
        self.device_id = device_id
        self.device_name = device_name
        self.device_status = device_status
        self.registered = Utils.get_datetime(registered)

    @staticmethod
    def get_list(json_data):
        devices = []

        for device in json_data.get("devices"):
            devices.append(
                Device(
                    customer_defined_name=device.get("customerDefinedName"),
                    device_class=device.get("deviceClass"),
                    device_id=device.get("deviceId"),
                    device_name=device.get("deviceName"),
                    device_status=device.get("deviceStatus"),
                    registered=device.get("registered")
                )
            )

        return devices
