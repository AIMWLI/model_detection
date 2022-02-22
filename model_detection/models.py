from django.db import models


class CommonInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    create_time = models.DateTimeField(default=None)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        # ordering = ['name']


class Record(CommonInfo):
    interface = models.CharField(max_length=128)
    source = models.CharField(max_length=128, default=None)
    weight = models.IntegerField(default=0)
    deleted = models.IntegerField(default=0)

    class Meta(CommonInfo.Meta):
        db_table = "model_record"
        managed = True

# class
