from dataclasses import dataclass

@dataclass
class ReportFiles:
    success_report_path: str
    failure_report_path: str