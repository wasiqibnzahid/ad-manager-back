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
            one_day_ago = today - timezone.timedelta(days=1)
            two_days_ago = today - timezone.timedelta(days=2)
            reports = Report.objects.all()

            # Process each report
            for report in reports:
                print(f"PROCESSING {report}")
                process_report(report.pk, report.start_date,
                               one_day_ago, report.ad_unit_ids, report.cpm_rate)
                report.end_date = one_day_ago
                report.save()
                print(f"Processed Report: {report}")
        except Exception as e:
            print(f"JOB FAILED - Error: {e}")
