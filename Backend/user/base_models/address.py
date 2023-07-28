from django.core.validators import RegexValidator
from django.db import models


class AbstractAddress(models.Model):
    phone_regex = RegexValidator(regex=r'^[1-9][0-9]{8,14}$',
                                 message="Phone number must not consist of space and requires country code. eg : "
                                         "989210000000")
    phone = models.CharField(validators=[phone_regex], max_length=16, unique=True)
    address = models.CharField(blank=True, null=True, max_length=80)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.address} : {self.phone}"
        # return "{} : {}".format(self.address)

    class Meta:
        abstract = True
