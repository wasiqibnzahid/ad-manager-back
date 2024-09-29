from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from users.models import Report
from users.create_report import process_report


# Assuming process_report is defined somewhere in your app


class Command(BaseCommand):
    help = 'Runs my periodic task to get and process reports'

    def handle(self, *args, **options):
        try:
            # Get today's date and calculate the date two days ago
            today = timezone.now().date()
            two_days_ago = today - timezone.timedelta(days=2)

            # Query the reports
            reports = Report.objects.filter(
                Q(end_date__gte=two_days_ago) | Q(report_id__isnull=True)
            )

            # Process each report
            for report in reports:
                print(f"PROCESSING {report}")
                # Call the process_report function with the required parameters
                process_report(report.report_id, report.start_date,
                               two_days_ago, report.ad_unit_ids, report.cpm_rate)

                # Log that the report has been processed
                print(f"Processed Report: {report}")
        except Exception as e:
            print(f"JOB FAILED - Error: {e}")
