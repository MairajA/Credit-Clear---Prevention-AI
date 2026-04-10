from django.conf import settings
from django.db import models


class EducationContent(models.Model):
    class ContentType(models.TextChoices):
        GUIDE = "guide", "Guide"
        VIDEO = "video", "Video"
        TEMPLATE = "template", "Template"
        COURSE = "course", "Course"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices, db_index=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserEducationProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="education_progress")
    content = models.ForeignKey(EducationContent, on_delete=models.CASCADE, related_name="progress_records")
    completion_percent = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False, db_index=True)
    last_viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "content")]
