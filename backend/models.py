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
    value = models.TextField()

    class Meta:
        managed = False
        db_table = "pen_felmeresek"
