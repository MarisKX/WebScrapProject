import re
from datetime import date
from django.db import models


class BaseModel(models.Model):
    name = models.CharField(blank=True, null=True, max_length=256)
    display_name = models.CharField(blank=False, null=True, max_length=256)

    def __str__(self):
        return self.name

    def get_display_name(self):
        return self.display_name

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.name = re.sub(r"[(), /-]", "_", self.display_name).lower()
        self.name = re.sub(r"\*", "x", self.name)
        super().save(*args, **kwargs)


class VehicleCategory(BaseModel):
    class Meta:
        verbose_name_plural = "Vehicle Categories"

    code = models.CharField(max_length=12)
    sort_order = models.IntegerField(default=0)


class Make(BaseModel):
    vehicle_category = models.ForeignKey(
        VehicleCategory, blank=True, null=True, on_delete=models.CASCADE
    )
    raw_make = models.CharField(blank=True, null=True, max_length=256)


class Model(BaseModel):
    make = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name="model",
    )
    raw_model = models.CharField(blank=True, null=True, max_length=256)


class BodyType(BaseModel):
    code = models.CharField(max_length=3)


class Color(BaseModel):
    pass


class FuelType(BaseModel):
    code = models.CharField(max_length=64)


class Vehicle(BaseModel):
    # General information
    licence_plate = models.CharField(max_length=8, unique=True, db_index=True)
    make = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name="cars",
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name="cars",
    )
    raw_name = models.CharField(blank=True, null=True, max_length=256)
    vehicle_category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # APK, insurance and status information
    first_reg = models.DateField(null=True, blank=True, db_index=True)
    first_reg_in_NL = models.DateField(null=True, blank=True)
    imported_in_NL = models.DateField(null=True, blank=True)
    apk = models.DateField(null=True, blank=True)
    valid_apk = models.BooleanField(default=True)
    insurance = models.BooleanField(default=False)
    exported = models.BooleanField(default=False, db_index=True)

    # Technical information
    engine_volume = models.CharField(max_length=18, blank=True, null=True)
    cylinder_count = models.CharField(max_length=2, blank=True, null=True)
    fuel_type = models.ManyToManyField(FuelType)
    kw = models.CharField(max_length=18, blank=True, null=True)
    hp = models.CharField(max_length=18, blank=True, null=True)
    kw2 = models.CharField(max_length=18, blank=True, null=True)
    hp2 = models.CharField(max_length=18, blank=True, null=True)
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        related_name="color",
        null=True,
        blank=True,
    )
    body_type = models.ForeignKey(
        BodyType,
        on_delete=models.SET_NULL,
        related_name="body_type",
        null=True,
        blank=True,
    )
    # Weight information
    curb_weight = models.CharField(max_length=20, blank=True, null=True)
    empty_weight = models.CharField(max_length=20, blank=True, null=True)
    max_weight_tech = models.CharField(max_length=20, blank=True, null=True)
    max_weight_legal = models.CharField(max_length=20, blank=True, null=True)
    gross_combination_weight = models.CharField(max_length=20, blank=True, null=True)
    trailer_with_brakes = models.CharField(
        max_length=20, blank=True, null=True, db_index=True
    )
    trailer_without_brakes = models.CharField(max_length=20, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    archived = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Combine Make and Model display names into Car's display name
        # print("Save method called!")
        if self.make and self.model:
            self.display_name = f"{self.make.display_name} {self.model.display_name}"
        self.raw_name = f"{self.make.raw_make} {self.model.raw_model}"

        # Assign default color if not set
        if not self.color:
            self.color = Color.objects.get(display_name="-")

        if self.kw is not None:
            try:
                # Remove "kW" and strip whitespace, handle decimal separator
                stripped_kw = self.kw.replace("kW", "").strip().replace(",", ".")
                # Convert to float and then to integer
                int_kw = int(float(stripped_kw))
                # Convert kW to hp and round to the nearest whole number
                int_hp = round(int_kw * 1.3410220888, 0)
                # Assign the formatted value
                self.hp = f"{int(int_hp)} Hp"
            except ValueError:
                print(f"Invalid kW value: {self.kw}")
                self.hp = None
        if self.kw2 is not None:
            try:
                # Remove "kW" and strip whitespace, handle decimal separator
                stripped_kw2 = self.kw2.replace("kW", "").strip().replace(",", ".")
                # Convert to float and then to integer
                int_kw2 = int(float(stripped_kw2))
                # Convert kW to hp and round to the nearest whole number
                int_hp2 = round(int_kw2 * 1.3410220888, 0)
                # Assign the formatted value
                self.hp2 = f"{int(int_hp2)} Hp"
            except ValueError:
                print(f"Invalid kW value: {self.kw}")
                self.hp2 = None
        # Check if APK date is valid or expired
        if self.apk is not None:
            self.valid_apk = self.apk >= date.today()  # Assign True or False
            # print(f"Setting valid_apk: {self.valid_apk}")
        else:
            self.valid_apk = False
            # print("APK date is None; setting valid_apk to False.")

        # Save the object
        super().save(*args, **kwargs)
