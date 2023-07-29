from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(("created_at"), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(
        ("modified_at"), auto_now=True, auto_now_add=False
    )

    class Meta:
        abstract = True
