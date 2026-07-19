from __future__ import annotations

import logging
import threading
from typing import Any, Callable

import paho.mqtt.client as mqtt

from configuration import Config


LOG = logging.getLogger("york_bridge.mqtt")
MessageHandler = Callable[[mqtt.MQTTMessage], None]
ConnectedHandler = Callable[[bool], None]
DisconnectedHandler = Callable[[str], None]


class MqttManager:
    def __init__(
        self,
        config: Config,
        *,
        on_message: MessageHandler,
        on_connected: ConnectedHandler,
        on_disconnected: DisconnectedHandler,
    ) -> None:
        self.config = config
        self.on_message_handler = on_message
        self.on_connected_handler = on_connected
        self.on_disconnected_handler = on_disconnected
        self.connected_event = threading.Event()
        self.stopping = False
        self.has_connected = False
        self.connected = False

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=config.client_id)
        self.client.reconnect_delay_set(
            min_delay=config.reconnect_min_seconds,
            max_delay=config.reconnect_max_seconds,
        )
        if config.mqtt_username:
            self.client.username_pw_set(config.mqtt_username, config.mqtt_password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.will_set(f"{config.base_topic}/bridge/availability", "offline", retain=True)

    def start(self) -> None:
        LOG.info("Connecting to MQTT broker %s:%s", self.config.mqtt_host, self.config.mqtt_port)
        self.client.connect_async(self.config.mqtt_host, self.config.mqtt_port, keepalive=60)
        self.client.loop_start()

    def wait_until_connected(self) -> bool:
        return self.connected_event.wait(self.config.startup_connect_timeout_seconds)

    def stop(self) -> None:
        self.stopping = True
        if self.connected:
            self.publish(f"{self.config.base_topic}/availability", "offline", retain=True)
            self.publish(f"{self.config.base_topic}/bridge/availability", "offline", retain=True)
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, topic: str, payload: Any, retain: bool = True) -> bool:
        if not self.connected:
            LOG.debug("Skipping MQTT publish while disconnected: %s", topic)
            return False
        info = self.client.publish(topic, str(payload), retain=retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            LOG.warning("MQTT publish failed for %s: rc=%s", topic, info.rc)
            return False
        return True

    def subscribe_commands(self) -> None:
        result, _ = self.client.subscribe(f"{self.config.base_topic}/+/set")
        if result != mqtt.MQTT_ERR_SUCCESS:
            LOG.error("Unable to subscribe to command topics: rc=%s", result)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        if reason_code != 0:
            LOG.error("MQTT connection failed: %s", reason_code)
            return
        reconnect = self.has_connected
        self.has_connected = True
        self.connected = True
        self.connected_event.set()
        LOG.info("%s to MQTT", "Reconnected" if reconnect else "Connected")
        self.subscribe_commands()
        self.on_connected_handler(reconnect)

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self.connected = False
        self.connected_event.clear()
        if self.stopping:
            LOG.info("Disconnected from MQTT")
        else:
            LOG.warning("MQTT disconnected (%s); automatic reconnect enabled", reason_code)
            self.on_disconnected_handler(str(reason_code))

    def _on_message(self, client: mqtt.Client, userdata: object, message: mqtt.MQTTMessage) -> None:
        self.on_message_handler(message)
