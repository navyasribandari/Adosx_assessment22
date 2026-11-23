from django.db import models


class Location(models.Model):
    # The ONLY source of the location -> org (tenant) mapping.
    location_id = models.CharField(max_length=32, unique=True)
    org_id = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=128, blank=True)


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=32, unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="a_records")
    event_date = models.DateField(null=True)
    category_code = models.CharField(max_length=32, blank=True)
    actor_id = models.CharField(max_length=32, null=True, blank=True)  # blank in CSV -> NULL
    base_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    adjustment = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    state = models.CharField(max_length=16)


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=64, unique=True)
    record_ref_raw = models.CharField(max_length=64, blank=True)       # original text
    # Cleaned ref. Deliberately NOT unique and NOT a ForeignKey: several entries may share
    # one record, and an orphan points at a record that does not exist in A.
    record_ref = models.CharField(max_length=32, null=True, db_index=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="b_entries")
    recorded_on = models.DateField(null=True)
    value_raw = models.CharField(max_length=64, blank=True)            # original text
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True)  # NULL = unknown
    label = models.CharField(max_length=128, blank=True)
