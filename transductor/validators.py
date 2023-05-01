from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from data_collector.modbus.settings import CSV_SCHEMA


def latitude_validator(value):
    if value < -90 or value > 90:
        msg = _(f"{value} is not a valid latitude")
        raise serializers.ValidationError(msg, code="invalid_value")


def longitude_validator(value):
    if value < -180 or value > 180:
        msg = _(f"{value} is not a valid longitude")
        raise serializers.ValidationError(msg, code="invalid_value")


def validate_csv_file(csv_data):
    headers = next(iter(csv_data), {}).keys()
    if not headers:
        msg = _("Empty CSV file")
        raise serializers.ValidationError(msg, code="invalid_csv")

    if len(set(headers)) != len(headers):
        msg = _("Duplicate headers in CSV file")
        raise serializers.ValidationError(msg, code="csv_duplicate_headers")

    missing_headers = set(CSV_SCHEMA) - set(headers)
    if missing_headers:
        msg = _(f"Invalid CSV no required headers. Missing headers: {missing_headers}")
        raise serializers.ValidationError(msg, code="csv_missing_headers")

    for row in csv_data:
        for key, value in row.items():
            if key not in CSV_SCHEMA:
                continue
            if value == "":
                msg = _(f"Field [{key} : {value}] value cannot be null.")
                raise serializers.ValidationError(msg, code="value_not_null")

            column_type = CSV_SCHEMA.get(key)
            try:
                column_type(value)
            except ValueError:
                msg = _(f"Unable to convert data type. Field [{key} : {value}] cannot be converted to {column_type}.")
                raise serializers.ValidationError(msg, code="type_not_convert")
