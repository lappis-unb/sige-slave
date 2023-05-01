from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException

from transductor.models import Transductor


class MeasurementParamsValidator:
    @staticmethod
    def get_fields():
        return [
            ("id", MeasurementParamsValidator.validate_id),
            ("start_date", MeasurementParamsValidator.validate_start_date),
            ("end_date", MeasurementParamsValidator.validate_end_date),
        ]

    @staticmethod
    def validate_query_params(params):
        fields = MeasurementParamsValidator.get_fields()
        errors = {}
        for field in fields:
            try:
                validation_function = field[1]
                param = params[field[0]]
                validation_function(param)

            except KeyError:
                # errors[field[0]] = _('It must have an %s argument' % field[0])
                pass
            except Exception as e:
                errors[field[0]] = e

        exception = APIException(
            errors,
            _("This id does not match with any Transductor"),
        )
        exception.status_code = 400

        if len(errors) != 0:
            raise exception

    @staticmethod
    def validate_id(transductor_id):
        try:
            Transductor.objects.get(id=transductor_id)
        except Transductor.DoesNotExist:
            raise Exception(
                _("This id does not match with any Transductor"),
            )

    @staticmethod
    def validate_start_date(start_date):
        try:
            timezone.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            message = "The start_date param must be a valid date in "
            message += "the format YYYY-MM-DD HH:MM:SS"
            raise Exception(
                _(message),
            )

    @staticmethod
    def validate_end_date(end_date):
        try:
            timezone.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            message = "The end_date param must be a valid date in "
            message += "the format YYYY-MM-DD HH:MM:SS"
            raise Exception(
                _(message),
            )
