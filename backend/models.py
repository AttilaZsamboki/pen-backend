from django.db import models

# Create your models here.
class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    script_name = models.TextField()
    time = models.DateTimeField()
    status = models.TextField()
    value = models.TextField()
    details = models.TextField()

    class Meta:
        managed = False
        db_table = "logs"

class Felmeresek(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.TextField()
    value = models.TextField(blank=True)
    adatlap_id = models.TextField()
    options = models.JSONField()
    type = models.CharField(max_length=255)
    section = models.TextField()

    class Meta:
        managed = False
        db_table = "pen_felmeresek"

class FelmeresekNotes(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.TextField()
    type = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    adatlap_id = models.TextField()

    class Meta:
        managed = False
        db_table = "pen_felmeresek_notes"