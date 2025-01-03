from django.utils.timezone import now

from rest_framework import serializers
from vehicles.models import (
    Vehicle,
    VehicleCategory,
)

# Util imports
from core.utilities.licence_plate_formatter import format_license_plate


class VehicleListSerializer(serializers.ModelSerializer):
    # Custom fields for nested data
    vehicle_category_display_name = serializers.CharField(
        source="vehicle_category.display_name", read_only=True
    )
    vehicle_category_code = serializers.CharField(
        source="vehicle_category.code", read_only=True
    )
    make_display_name = serializers.CharField(
        source="make.display_name", read_only=True
    )
    model_display_name = serializers.CharField(
        source="model.display_name", read_only=True
    )
    color_display_name = serializers.CharField(
        source="color.display_name", read_only=True
    )
    display_fuel_types = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "licence_plate",
            "vehicle_category_display_name",
            "vehicle_category_code",
            "make_display_name",
            "model_display_name",
            "first_reg",
            "first_reg_in_NL",
            "imported_in_NL",
            "color_display_name",
            "insurance",
            "apk",
            "display_fuel_types",
            "engine_volume",
            "cylinder_count",
            "exported",
        ]

    def get_display_fuel_types(self, obj):
        # Fetch related fuel types and replace "Undefined" with "-"
        fuel_types = obj.fuel_type.values_list("display_name", flat=True)
        if fuel_types:
            return "/".join(fuel if fuel != "undefined" else "-" for fuel in fuel_types)
        return "-"  # Default to "-" if no fuel types are defined

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the request includes the `exported` parameter
        request = self.context.get("request")
        if request:
            include_exported = (
                request.query_params.get("exported", "false").lower() == "true"
            )
            if not include_exported:
                # Remove the `exported` field if include_exported is False
                representation.pop("exported", None)
        return representation


class VehicleDetailSerializer(serializers.ModelSerializer):
    # Custom fields for nested data
    vehicle_category_display_name = serializers.CharField(
        source="vehicle_category.display_name", read_only=True
    )
    vehicle_category_code = serializers.CharField(
        source="vehicle_category.code", read_only=True
    )
    vehicle_body_type = serializers.CharField(
        source="body_type.display_name", read_only=True
    )
    vehicle_body_type_code = serializers.CharField(
        source="body_type.code", read_only=True
    )
    make_display_name = serializers.CharField(
        source="make.display_name", read_only=True
    )
    model_display_name = serializers.CharField(
        source="model.display_name", read_only=True
    )
    color_display_name = serializers.CharField(
        source="color.display_name", read_only=True
    )
    display_fuel_types = serializers.SerializerMethodField()
    formatted_license_plate = serializers.SerializerMethodField()
    last_updated_human = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = "__all__"  # Include all fields plus the custom ones
        extra_fields = ["formatted_license_plate"]  # Explicitly declare the added field

    def get_display_fuel_types(self, obj):
        """Returns a human-readable string of fuel types for the vehicle."""
        fuel_types = obj.fuel_type.values_list("display_name", flat=True)
        if fuel_types:
            return "/".join(fuel if fuel != "undefined" else "-" for fuel in fuel_types)
        return "-"  # Default to "-" if no fuel types are defined

    def get_formatted_license_plate(self, obj):
        """
        Returns the formatted license plate using the formatter function.
        """

        return format_license_plate(obj.licence_plate)

    def get_last_updated_human(self, obj):
        """
        Format the `last_updated` field to be more human-friendly.
        """
        if obj.last_updated:
            # Format the date and time
            formatted_time = obj.last_updated.strftime("%d-%m-%Y %H:%M")
            # Calculate the time difference
            time_diff = now() - obj.last_updated
            total_seconds = time_diff.total_seconds()
            hours = total_seconds // 3600
            days = time_diff.days

            # Add a human-friendly suffix
            if hours < 2:
                return f"{formatted_time} (just now)"
            elif hours < 6:
                return f"{formatted_time} (less than 6 hours ago)"
            elif days < 1:
                return f"{formatted_time} (less than a day ago)"
            elif days == 1:
                return f"{formatted_time} (yesterday)"
            elif 2 <= days < 7:
                return f"{formatted_time} (a few days ago)"
            elif 7 <= days < 30:
                return f"{formatted_time} (more than a week ago)"
            else:
                return f"{formatted_time} (more than a month ago)"
        return None


class VehicleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCategory
        fields = ["name", "display_name"]
