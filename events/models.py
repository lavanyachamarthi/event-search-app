from django.db import models


class Event(models.Model):
    serialno = models.BigIntegerField(null=True, db_index=True)
    version = models.IntegerField(null=True)
    account_id = models.CharField(max_length=64, null=True, db_index=True)
    instance_id = models.CharField(max_length=64, null=True, db_index=True)
    srcaddr = models.CharField(max_length=64, null=True, db_index=True)
    dstaddr = models.CharField(max_length=64, null=True, db_index=True)
    protocol = models.CharField(max_length=32, null=True, db_index=True)
    packets = models.BigIntegerField(null=True)
    bytes = models.BigIntegerField(null=True)
    starttime = models.BigIntegerField(null=True, db_index=True)
    endtime = models.BigIntegerField(null=True, db_index=True)
    action = models.CharField(max_length=32, null=True, db_index=True)
    log_status = models.CharField(max_length=32, null=True)
    srcport = models.IntegerField(null=True, db_index=True)
    dstport = models.IntegerField(null=True, db_index=True)

    file_name = models.CharField(max_length=255, db_index=True)
    raw_line = models.TextField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["srcaddr", "dstaddr", "action"]),
            models.Index(fields=["starttime", "endtime"]),
        ]

    def __str__(self) -> str:
        return f"{self.srcaddr} -> {self.dstaddr} | {self.action}"

# Create your models here.
