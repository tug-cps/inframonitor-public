from .event import ReportEvent


class SensorEvent(ReportEvent):
    def __init__(self, sensor, status: int) -> None:
        super().__init__()
        self.sensor = sensor
        self.status = status

    def describe_status(self) -> str:
        if self.status == 0:
            return "OK"
        elif self.status == 1:
            return "Reading is > 1.3 * all time prediction"
        elif self.status == 2:
            return "Reading is higher than prediction for >= 3 hours"
        elif self.status == 4:
            return "Reading is never <= minimal predicted value between 22:00 and 04:00"
        elif self.status == 1024:
            return "Reading for sensor did not change in the last >= 24h"
        raise Exception("Unknown status code")

    def describe_sensor(self) -> str:
        text = f'{self.sensor["building"]["address"]["value"]["streetAddress"]} - {self.sensor["name"]}'
        description = self.sensor.get('description')
        if description:
            text += f' ({description})'

        return text

    def describe(self) -> str:
        return self.describe_sensor() + ": " + self.describe_status()

    def get_status(self) -> int:
        return self.status
