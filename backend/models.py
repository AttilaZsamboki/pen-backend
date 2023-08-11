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
    
class DatauploadTabletemplates(models.Model):
    id = models.BigAutoField(primary_key=True)
    table = models.CharField(max_length=30)
    pkey_col = models.CharField(max_length=30, blank=True, null=True)
    skiprows = models.CharField(max_length=10)
    append = models.CharField(max_length=40)
    source_column_names = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataupload_tabletemplates'