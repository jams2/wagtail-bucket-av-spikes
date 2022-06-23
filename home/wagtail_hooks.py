from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from wagtail import hooks
from wagtail.images import get_image_model
from wagtail.documents import get_document_model
from wagtail.log_actions import log, LogFormatter
from wagtail.models import ModelLogEntry

from .models import AVScanStatus


@hooks.register("register_log_actions")
def register_av_scan_logging(actions):
    actions.register_model(AVScanStatus, ModelLogEntry)

    @actions.register_action("wagtail_bucket_av.scan_pending")
    class PendingAVScanFormatter(LogFormatter):
        label = "AV Scan Pending"

        def format_message(self, log_entry):
            return (
                f"<{log_entry.data['model']}: {log_entry.data['title']}> scan pending"
            )


@receiver(post_save)
def log_av_scan_pending(sender, **kwargs):
    if sender not in (get_image_model(), get_document_model()):
        return

    instance = kwargs["instance"]
    content_type = ContentType.objects.get_for_model(sender)
    if AVScanStatus.objects.filter(
        content_type=content_type, object_id=instance.pk
    ).exists():
        return

    AVScanStatus.objects.create(
        object_title=instance.title,
        object_id=instance.pk,
        content_type=content_type,
        scan_status=AVScanStatus.Status.PENDING,
    )

    log_data = {
        "title": instance.title,
        "model": content_type.model,
    }
    log(instance, "wagtail_bucket_av.scan_pending", data=log_data)
