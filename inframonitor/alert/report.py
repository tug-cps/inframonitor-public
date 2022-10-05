from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List

from .event import ReportEvent


class ReportPrinter:
    def __init__(self, report) -> None:
        super().__init__()
        self.report = report

    @abstractmethod
    def print(self):
        pass


class PlainReportPrinter(ReportPrinter):
    def print(self):
        txt = ""
        for section in self.report.sections:
            txt += "\n## " + section.header + "\n"
            for entry in section.entries:
                txt += "* " + entry + "\n"
        return txt


class HTMLReportPrinter(ReportPrinter):
    def print(self):
        html = "<html><head></head><body>"
        for section in self.report.sections:
            html += "<h1>" + section.header + "</h1>"
            html += "<ul>"
            for entry in section.entries:
                html += "<li>" + entry + "</li>"
            html += "</ul>"
        html += "</body></html>"
        return html


@dataclass
class Section:
    header: str
    entries: List[str] = field(default=list)


@dataclass
class Report:
    header: str = ""
    sections: List[Section] = field(default_factory=list)


def build_report(new_events: List[ReportEvent],
                 persisting_events: List[ReportEvent],
                 fixed_events: List[ReportEvent]) -> Report:
    def build_section(section_prefix, section_events: List[ReportEvent]) -> Section:
        return Section(f'{len(section_events)} {section_prefix} error(s)',
                       [event.describe() for event in section_events])

    report = Report(header="Report for inframonitor.tugraz.at")
    if len(new_events) > 0 or len(persisting_events) > 0:
        report.header += f' with {len(new_events)} new error(s), {len(persisting_events)} persisting error(s) and {len(fixed_events)} fixed error(s)'
    else:
        report.header += " - all sensors back to normal"

    if len(new_events) > 0:
        report.sections.append(build_section("NEW", new_events))
    if len(persisting_events) > 0:
        report.sections.append(build_section("PERSISTING", persisting_events))
    if len(fixed_events) > 0:
        report.sections.append(build_section("FIXED", fixed_events))

    return report
