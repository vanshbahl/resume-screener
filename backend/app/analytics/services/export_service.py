import csv
import io
from app.analytics.schemas.analytics import ReportResponse

class ExportService:
    def export_report_to_csv(self, report: ReportResponse) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(report.columns)
        
        # Write rows
        for row in report.rows:
            writer.writerow([row.get(col, "") for col in report.columns])
            
        return output.getvalue()
