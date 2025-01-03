from django.contrib import admin
from .models import (
    Make,
    Model,
    Vehicle,
    Color,
    FuelType,
    VehicleCategory,
    BodyType,
)
from core.models import (
    LastPlateIssued,
    UncheckedPlates,
    LastPlatechecked,
    RecheckForAPKPlates,
)


class ModelAdmin(admin.TabularInline):

    model = Model
    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "display_name",
        "name",
        "raw_model",
    )


class MakeAdmin(admin.ModelAdmin):

    inlines = [
        ModelAdmin,
    ]
    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "display_name",
        "name",
        "raw_make",
    )


class ColorAdmin(admin.ModelAdmin):

    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "display_name",
        "name",
    )


class VehicleCategoryAdmin(admin.ModelAdmin):

    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "code",
        "display_name",
        "sort_order",
        "name",
    )


class BodyTypeAdmin(admin.ModelAdmin):

    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "code",
        "display_name",
        "name",
    )


class FuelTypeAdmin(admin.ModelAdmin):

    readonly_fields = ("name",)
    ordering = ("name",)
    list_display = (
        "display_name",
        "code",
        "name",
    )


class VehicleAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "General Information",
            {
                "fields": [
                    "licence_plate",
                    ("make", "model"),
                    "vehicle_category",
                ],
            },
        ),
        (
            "Registration Information",
            {
                "classes": ["collapse", "wide"],
                "fields": ["first_reg", "first_reg_in_NL", "imported_in_NL"],
            },
        ),
        (
            "Status Data",
            {
                "classes": ["collapse"],
                "fields": [("valid_apk", "apk"), "insurance", "exported"],
            },
        ),
        (
            "Technical Data",
            {
                "classes": ["collapse"],
                "fields": [
                    ("engine_volume", "cylinder_count"),
                    ("kw", "hp"),
                    "fuel_type",
                    "color",
                    "body_type",
                ],
            },
        ),
        (
            "Weight Data",
            {
                "classes": ["collapse"],
                "fields": [
                    "curb_weight",
                    "empty_weight",
                    "max_weight_tech",
                    "max_weight_legal",
                    "gross_combination_weight",
                    "trailer_with_brakes",
                    "trailer_without_brakes",
                ],
            },
        ),
    ]
    readonly_fields = ("name",)
    list_per_page = 200
    ordering = (
        "first_reg",
        "make",
        "model",
    )
    list_display = (
        "licence_plate",
        "vehicle_category_display_name",
        "make",
        "model",
        "first_reg",
        "first_reg_in_NL",
        "imported_in_NL",
        "color",
        "valid_apk",
        "insurance",
        "apk",
        "display_fuel_types",
        "engine_volume",
        "cylinder_count",
        "display_name",
        "name",
        "raw_name",
        "exported",
        "last_updated",
    )

    def display_fuel_types(self, obj):
        """Return a comma-separated list of fuel types for the car."""
        return "/".join([fuel.display_name for fuel in obj.fuel_type.all()])

    display_fuel_types.short_description = "Fuel Type"

    def vehicle_category_display_name(self, obj):
        """Return the display name of the vehicle category for the car's make."""
        if obj.make and hasattr(obj.make, "vehicle_category"):
            return obj.make.vehicle_category.display_name
        return "N/A"  # Return a default value if not available

    vehicle_category_display_name.short_description = "Vehicle Category"


class LastPlatecheckedAdmin(admin.ModelAdmin):
    list_display = (
        "plate",
        "pattern",
    )


class UncheckedPlatesAdmin(admin.ModelAdmin):
    list_display = ("plate",)


class LastPlateIssuedAdmin(admin.ModelAdmin):
    list_display = (
        "plate",
        "pattern",
        "issued",
    )


class RecheckForAPKPlatesAdmin(admin.ModelAdmin):
    list_display = (
        "plate",
        "vehicle",
        "first_reg",
        "apk",
    )


admin.site.register(Make, MakeAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(VehicleCategory, VehicleCategoryAdmin)
admin.site.register(BodyType, BodyTypeAdmin)
admin.site.register(FuelType, FuelTypeAdmin)
admin.site.register(LastPlatechecked, LastPlatecheckedAdmin)
admin.site.register(UncheckedPlates, UncheckedPlatesAdmin)
admin.site.register(LastPlateIssued, LastPlateIssuedAdmin)
admin.site.register(RecheckForAPKPlates, RecheckForAPKPlatesAdmin)
