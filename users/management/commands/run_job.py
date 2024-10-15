from django.core.management.base import BaseCommand
import datetime
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
            reports = Report.objects.all()
            self.log()
            # Process each report
            for report in reports:
                print(f"PROCESSING {report}")
                process_report(report.pk, two_days_ago,
                               two_days_ago, report.ad_unit_ids.split(","), report.cpm_rate)
                report.end_date = two_days_ago
                report.save()
                log_file_path = '/root/job_log.txt'
                current_time = datetime.datetime.now()
                timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                with open(log_file_path, 'a') as file:
                    file.write(f"Job finished for {two_days_ago} for report {
                               report.pk} {report.name}: {timestamp}\n")
                print(f"Processed Report: {report}")
        except Exception as e:
            print(f"JOB FAILED - Error: {e}")

    def log(self):
        current_time = datetime.datetime.now()

        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        log_file_path = '/root/job_log.txt'
        with open(log_file_path, 'a') as file:
            file.write(f"Job ran on: {timestamp}\n")

        print(f"Timestamp added to {log_file_path}")
