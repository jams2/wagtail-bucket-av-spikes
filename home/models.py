from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from wagtail.models import Page


class HomePage(Page):
    pass


class AVScanStatus(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SAFE = "SAFE", "Safe"
        MALICIOUS = "MALICIOUS", "Malicious"

    object_title = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")
    scan_status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return f"{self.object_title}: {self.get_scan_status_display()}"

    class Meta:
        indexes = [models.Index(fields=("content_type", "object_id"))]
