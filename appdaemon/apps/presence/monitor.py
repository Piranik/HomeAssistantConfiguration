import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
import globals
from globals import PEOPLE
from base import Base
import json

class Monitor(Base):

    def initialize(self) -> None:
        """Initialize."""
        super().initialize()

        self.listen_state(self.trigger_departure_scan, "binary_sensor.front_door")
        self.listen_state(self.bt_change, "device_tracker.hallway_limych_ahphoneb_bt")
        self.listen_state(self.bt_change, "device_tracker.bedroom_limych_ahphoneb_bt")
        self.listen_state(self.monitor_status, "sensor.monitor_hallway")

    def bt_change(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.log(f"Bt tracker change from monitor. {entity} was {old}, now {new}")
            # self.notification_manager.log_monitor(message = f"Bt tracker change from monitor. {entity} was {old}, now {new}")

    def trigger_departure_scan(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.log("Initiating arrive scan in 5 sec")
            self.log("Initiating departure scan in 30 sec")

            self.run_in(self.scan_arrive, 5)
            self.run_in(self.scan_arrive, 30)

            self.run_in(self.scan_depart, 30)

            self.run_in(self.scan_arrive, 60)

            self.run_in(self.scan_depart, 60)
            self.run_in(self.scan_depart, 90)
            self.run_in(self.scan_depart, 120)

    def monitor_status(self, entity, attribute, old, new, kwargs):
        if new != old:
            # self.notification_manager.log_monitor(message = f"Monitor is {new}")
            if new == "online":
                self.run_in(self.scan_arrive, 5)
                self.run_in(self.scan_arrive, 30)
                self.run_in(self.scan_arrive, 60)

    def scan_arrive(self, kwargs):
        # self.notification_manager.log_monitor(message = f"Requested scan for arrival.")
        self.call_service("mqtt/publish", topic = "presence/scan/ARRIVE")

    def scan_depart(self, kwargs):
        # self.notification_manager.log_monitor(message = f"Requested scan for departure.")
        self.call_service("mqtt/publish", topic = "presence/scan/DEPART")
