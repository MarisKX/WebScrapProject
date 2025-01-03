from django.urls import path
from vehicles.views import (
    VehicleListView,
    VehicleDetailView,
    UniqueVehicleCategoriesView,
    VehicleCategoryCombinedCountView,
    VehicleYearStatsView,
    VehicleCategoryStatsView,
)

urlpatterns = [
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
    path(
        "vehicle-categories/",
        UniqueVehicleCategoriesView.as_view(),
        name="vehicle-categories",
    ),
    path(
        "vehicle-categories-count/",
        VehicleCategoryCombinedCountView.as_view(),
        name="vehicle-categories-count",
    ),
    path(
        "vehicle-first-reg-year-stats/",
        VehicleYearStatsView.as_view(),
        name="vehicle-first-reg-year-stats",
    ),
    path(
        "vehicle-category-stats/",
        VehicleCategoryStatsView.as_view(),
        name="vehicle-category-stats",
    ),
]
