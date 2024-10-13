# # Import the library.
# import tempfile
# from googleads import ad_manager

# # Initialize a client object, by default uses the credentials in ~/googleads.yaml.
import tempfile
import csv
import gzip
from .models import Report, Record
from googleads import ad_manager
from datetime import datetime, timedelta
from dateutil import parser  # Make sure to import the dateutil parser
import pandas as pd
import os
from django.utils import timezone

client = ad_manager.AdManagerClient.LoadFromStorage("~/googleads.yaml")


def get_unit_ids(item):
    return int(item["value"])


def fetch_ad_units():

    # Initialize the Ad Manager client
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Initialize the appropriate service
    ad_unit_service = client.GetService('InventoryService', version='v202408')

    # Create a statement to select ad units.
    statement = ad_manager.StatementBuilder(version='v202408')

    # Retrieve a small number of ad units at a time, paging through until all ad units have been retrieved.
    response = ad_unit_service.getAdUnitsByStatement(statement.ToStatement())
    results = []
    if 'results' in response and len(response['results']):
        for ad_unit in response['results']:
            results.append({
                "label": ad_unit['name'],
                "value": int(ad_unit["id"])
            })
    return results


def process_report(id, start_date, end_date, ad_unit_ids, cpm_rate):
    client = ad_manager.AdManagerClient.LoadFromStorage("~/googleads.yaml")
    today = timezone.now().date()
# Check if the given date is equal to or greater than today
    if end_date >= today:
        # If it is today or a future date, change it to yesterday
        end_date = today - timedelta(days=2)
    report_job = {
        "reportQuery": {
            "dimensions": [
                "DATE",
                "AD_UNIT_ID"
            ],
            "columns": [
                "AD_SERVER_IMPRESSIONS",
                "AD_SERVER_CLICKS",
                "AD_SERVER_CTR",
                "AD_UNIT_ID",
                "AD_UNIT_NAME"
            ],
            "dateRangeType": "CUSTOM_DATE",
            "startDate": {
                "year": start_date.year,
                "month": start_date.month,
                "day": start_date.day
            },
            "endDate": {
                "year": end_date.year,
                "month": end_date.month,
                "day": end_date.day
            }
        }
    }
    if len(ad_unit_ids) > 0:
        # Build the WHERE statement using ad_unit_ids
        statement = (ad_manager.StatementBuilder(version='v202408')
                     .Where("AD_UNIT_ID IN (%s)" % ','.join(map(str, ad_unit_ids)))
                     .Limit(None)
                     .Offset(None))
        report_job["reportQuery"]["statement"] = statement.ToStatement()
    print(f"report_job {report_job}")
    return;
    report_downloader = client.GetDataDownloader(version='v202408')
    report_job_id = report_downloader.WaitForReport(report_job)


    with tempfile.NamedTemporaryFile(suffix='.csv.gz', mode='wb', delete=False) as report_file:
        report_downloader.DownloadReportToFile(
            report_job_id, 'CSV_DUMP', report_file)
    try:
        # Process the CSV file and save each record
        report = Report.objects.get(id=id)
        df = pd.read_csv(report_file.name, compression='gzip')
        for _index, row in df.iterrows():
            # Headers are used by default

            # Assuming columns: Date, AdUnitID, AdUnitName, Impressions, Clicks, CTR
            # Adjust index if CSV structure changes
            date = datetime.strptime(row[0], '%Y-%m-%d').date()
            ad_unit_id = str(row[1])
            ad_unit_name = row[2]
            impressions = int(row[3])
            clicks = str(row[4])
            ctr = float(row[5])
            # Calculate revenue using the formula (cpm_rate * impressions) / 1000
            revenue = (cpm_rate * impressions) / 1000
            # Save the record in the database
            Record.objects.update_or_create(
                report=report,
                date=date,
                ad_unit_id=ad_unit_id,
                ad_unit_name=ad_unit_name,
                defaults={
                    'impressions': str(impressions),
                    'clicks': clicks,
                    'ctr': ctr,
                    'revenue': str(revenue),
                }
            )
        report.status = 'Done'
        report.save()
    finally:
        if (os.path.exists(report_file.name)):
            os.remove(report_file.name)
