from django.db import models


class LastPlatechecked(models.Model):
    class Meta:
        verbose_name_plural = "Last Plate checked"

    pattern = models.CharField(max_length=6)
    plate = models.CharField(max_length=6)


class UncheckedPlates(models.Model):
    plate = models.CharField(max_length=6)


class LastPlateIssued(models.Model):
    class Meta:
        verbose_name_plural = "Last Plate Issued"

    pattern = models.CharField(max_length=6)
    plate = models.CharField(max_length=6)
    issued = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class RecheckForAPKPlates(models.Model):
    plate = models.CharField(max_length=6)
    vehicle = models.CharField(max_length=256, null=True, blank=True)
    first_reg = models.DateField(null=True, blank=True)
    apk = models.DateField(null=True, blank=True)
    checked_apk = models.DateField(null=True, blank=True)
