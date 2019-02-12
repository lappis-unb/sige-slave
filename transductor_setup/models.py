from django.db import models
from boogie.rest import rest_api
from django.contrib.postgres.fields import ArrayField


# @rest_api()
class TransductorSetup(models.Model):
    """
    Class responsible to define a transductor model which contains
    crucial informations about the transductor itself.

    Attributes:
        firmware_version (str): Transductor's current firmware version.
        primary_pt_ratio (int): Primary potential transformer ratio.
        secondary_pt_ratio (int): Secondary potential transformer ratio.
        multiplication_factor_pt_ratio (int): Potential transformer
            multiplication ratio.
        primary_ct_ratio (int): Primary current transformer ratio.
        secondary_ct_ratio (int): Secondary current transformer ratio.
        multiplication_factor_ct_factor (int): Current transformer
            multiplication ratio
        start_peak_time (Datetime): Energy peak time beginning.
        start_off_peak_time (Datetime): Energy off-peak time beginning.
        holidays (list): List of years holidays.
        pt_ratio (float): Potential transformer ratio.
        ct_ratio (float): Current transformer ratio.
        variables_integration_time (int): Variables integration time.

    Example of use:

    >>>
    """

    firmware_version = models.CharField(default=1, max_length=20)

    pt_ratio = models.FloatField(default=0)
    primary_pt_ratio = models.IntegerField(default=0)
    secondary_pt_ratio = models.IntegerField(default=0)
    multiplication_factor_pt_ratio = models.IntegerField(default=0)

    ct_ratio = models.FloatField(default=0)
    primary_ct_ratio = models.IntegerField(default=0)
    secondary_ct_ratio = models.IntegerField(default=0)
    multiplication_factor_ct_factor = models.IntegerField(default=0)

    variables_integration_time = models.IntegerField(default=1)

    start_peak_time = models.DateTimeField()
    start_off_peak_time = models.DateTimeField()

    holidays = ArrayField(models.DateTimeField())

    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="transductor_setup",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Setup informations about the Transductor #' + \
            self.transductor.serial_number

    def get_transductor_setup(values_list, transductor):
        """
        Method responsible to save transductor's setup information.
        Args:
            values_list (list): The list with all important measurements values.
            transductor (EnergyTransductor): Transductor owning these settings.
        Return:
            None
        """

        transductor_setup = TransductorSetup()

        transductor_setup.firmware_version = values_list[0]
        transductor_setup.primary_pt_ratio = values_list[1]
        transductor_setup.secondary_pt_ratio = values_list[2]
        transductor_setup.multiplication_factor_pt_ratio = values_list[3]
        transductor_setup.primary_ct_ratio = values_list[4]
        transductor_setup.secondary_ct_ratio = values_list[5]
        transductor_setup.multiplication_factor_ct_factor = values_list[6]
        transductor_setup.start_peak_time = values_list[7]
        transductor_setup.start_off_peak_time = values_list[8]
        transductor_setup.holidays = values_list[9]
        transductor_setup.pt_ratio = values_list[10]
        transductor_setup.ct_ratio = values_list[11]
        transductor_setup.variables_integration_time = values_list[12]

        transductor_setup.transductor = transductor

        transductor_setup.save()
