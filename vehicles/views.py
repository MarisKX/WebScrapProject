# General imports
from datetime import datetime

# Djnago imports
from django.db.models import Count
from django.db.models.functions import ExtractYear

# DRF imports
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response

# Custom models imports
from vehicles.models import (
    Vehicle,
    VehicleCategory,
)

# Custom serializers imports
from vehicles.serializers import (
    VehicleListSerializer,
    VehicleDetailSerializer,
    VehicleCategorySerializer,
)

# Util imports
from core.pagination import CustomPageNumberPagination

# Other imports
from collections import defaultdict


class VehicleListView(ListAPIView):
    queryset = Vehicle.objects.select_related(
        "make", "model", "vehicle_category", "color"
    ).prefetch_related("fuel_type")
    serializer_class = VehicleListSerializer
    pagination_class = CustomPageNumberPagination  # Add pagination

    sortable_fields = {
        "licence_plate": "licence_plate",
        "vehicle_category_display_name": "vehicle_category__display_name",
        "make_display_name": "make__display_name",
        "model_display_name": "model__display_name",
        "color_display_name": "color__display_name",
    }

    def get_queryset(self):
        # Retrieve filter parameters
        sort_by = self.request.query_params.get("sort_by", None)
        order = self.request.query_params.get("order", "asc")
        search = self.request.query_params.get("search", "")
        search_field = self.request.query_params.get("search_field", "")
        include_exported = (
            self.request.query_params.get("exported", "false").lower() == "true"
        )

        queryset = self.queryset

        # Apply search if both field and term are specified
        if search and search_field:
            field_lookup = (
                f"{self.sortable_fields.get(search_field, search_field)}__icontains"
            )
            queryset = queryset.filter(**{field_lookup: search})

        # Filter based on the exported field
        if not include_exported:
            queryset = queryset.filter(exported=False)

        # Determine the sort field(s)
        if sort_by:
            sort_field = self.sortable_fields.get(sort_by, sort_by)
            if order == "desc":
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)
        else:
            # Default sort by multiple fields
            default_sort_fields = ["first_reg", "make__display_name"]
            if order == "desc":
                default_sort_fields = [f"-{field}" for field in default_sort_fields]
            queryset = queryset.order_by(*default_sort_fields)

        return queryset

    def list(self, request, *args, **kwargs):
        # Dynamically adjust the response based on the exported filter
        include_exported = (
            request.query_params.get("exported", "false").lower() == "true"
        )

        # Call the parent class's list method to get the response
        response = super().list(request, *args, **kwargs)

        # Dynamically adjust sortable fields
        sortable_fields = {
            key: {"id": value, "label": key.replace("_", " ").capitalize()}
            for key, value in self.sortable_fields.items()
        }

        if not include_exported:
            # Remove the 'exported' field if vehicles are not exported
            sortable_fields.pop("exported", None)

        response.data["sortable_fields"] = sortable_fields
        return response

    def get_serializer_context(self):
        # Pass the request to the serializer's context
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class VehicleDetailView(RetrieveAPIView):
    queryset = Vehicle.objects.select_related(
        "make", "model", "vehicle_category", "color"
    ).prefetch_related("fuel_type")
    serializer_class = VehicleDetailSerializer


class UniqueVehicleCategoriesView(APIView):

    def get(self, request):
        # Query distinct name and display_name pairs
        categories = (
            VehicleCategory.objects.values("name", "display_name")
            .distinct()
            .order_by("sort_order")
        )

        # Serialize the data
        return Response(categories)


class VehicleCategoryCombinedCountView(APIView):
    def get(self, request):
        # Annotate each category with the count of related vehicles and include sort_order
        categories = (
            VehicleCategory.objects.annotate(vehicle_count=Count("vehicle"))
            .values("display_name", "vehicle_count", "sort_order")
            .order_by("sort_order")  # Ensure sorting by sort_order
        )

        # Combine counts by display_name
        combined_counts = defaultdict(lambda: {"vehicle_count": 0, "sort_order": None})
        total_vehicle_count = 0  # Track total count

        for category in categories:
            combined_counts[category["display_name"]]["vehicle_count"] += category[
                "vehicle_count"
            ]
            combined_counts[category["display_name"]]["sort_order"] = category[
                "sort_order"
            ]
            total_vehicle_count += category["vehicle_count"]  # Add to total count

        # Convert to the desired response format and sort by sort_order
        result = sorted(
            [
                {
                    "display_name": display_name,
                    "vehicle_count": data["vehicle_count"],
                }
                for display_name, data in combined_counts.items()
            ],
            key=lambda x: combined_counts[x["display_name"]][
                "sort_order"
            ],  # Sort by stored sort_order
        )

        # Add total count to the response
        response_data = {
            "categories": result,
            "total_vehicle_count": total_vehicle_count,
        }

        # Return the combined data
        return Response(response_data)


class VehicleYearStatsView(APIView):
    """
    API endpoint to retrieve vehicle counts grouped by the year of first registration.
    Includes all years from (current year - 100) to the current year, with older years aggregated.
    """

    def get(self, request, *args, **kwargs):
        # Get the current year
        current_year = datetime.now().year

        # Dynamically calculate the start year (100 years ago)
        start_year = (
            current_year - 99
        )  # Start from 1925 for a 100-year range (current year included)
        older_than_year = start_year - 1  # Year before the start year

        # Generate a list of years from (current year - 99) to the current year
        years_range = list(range(start_year, current_year + 1))

        # Query to extract year from 'first_reg' and count occurrences
        vehicles = (
            Vehicle.objects.annotate(year=ExtractYear("first_reg"))
            .values("year")
            .annotate(count=Count("id"))
        ).exclude(archived=True)

        # Initialize the result dictionary with "1924 and older" first
        sorted_result = {f"{older_than_year} and older": 0}
        print(sorted_result)

        # Add all years from the dynamic range with counts initialized to 0
        sorted_result.update({str(year): 0 for year in years_range})

        # Loop through query results and categorize data
        for item in vehicles:
            year = item["year"]
            count = item["count"]

            if year is None:
                # Skip entries without a year
                continue

            if year < start_year:  # Aggregate vehicles from 1924 and earlier
                sorted_result[f"{older_than_year} and older"] += count
                print(sorted_result)
            else:
                sorted_result[str(year)] = count

        # Return the response
        return Response(sorted_result)


class VehicleCategoryStatsView(APIView):
    """
    API endpoint to retrieve vehicle counts and percentages grouped by category.
    """

    def get(self, request, *args, **kwargs):
        # Query the total count of all vehicles
        total_count = Vehicle.objects.count()

        # Group by vehicle category and count each category
        category_stats = (
            Vehicle.objects.values("vehicle_category__display_name")
            .annotate(count=Count("id"))
            .order_by("-count")  # Order by count descending
        ).exclude(archived=True)

        # Prepare the response data
        results = []
        for item in category_stats:
            category_name = item["vehicle_category__display_name"] or "Unknown Category"
            count = item["count"]
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            results.append(
                {
                    category_name: {
                        "count": count,
                        "percentage": f"{percentage:.2f}%",  # Format to two decimal places
                    }
                }
            )

        return Response(results)
