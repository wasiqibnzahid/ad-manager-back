from django.contrib.auth.models import User
from django.db import models


class NormalUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    report_id = models.IntegerField(null=True)

    def __str__(self):
        return self.user.username


class Report(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    ad_unit_ids = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cpm_rate = models.FloatField(null=True)
    status = models.CharField(
        max_length=20, default='Processing')
    name = models.CharField(default="", max_length=255)

    def __str__(self):
        return f"Report {self.start_date} - {self.end_date}"


class Record(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    date = models.DateField()
    ad_unit_id = models.CharField(max_length=100)
    ad_unit_name = models.CharField(max_length=255)
    impressions = models.CharField(max_length=100)
    clicks = models.CharField(max_length=100)
    ctr = models.FloatField()
    revenue = models.CharField(default="0", max_length=100)

    def __str__(self):
        return f"Record for {self.report.name} on {self.date} - value {self.impressions} for unit - {self.ad_unit_name}"
