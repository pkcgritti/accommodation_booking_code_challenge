from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    name = "accommodation_booking"

    def ready(self):
        from accommodation_booking.container import ApplicationContainer

        container = ApplicationContainer()
        container.wire(
            modules=["bookings.views"],
            packages=["accommodation_booking.application.commands"],
        )
