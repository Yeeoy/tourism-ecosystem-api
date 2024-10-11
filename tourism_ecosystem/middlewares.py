import uuid

from django.urls import resolve
from django.utils import timezone

from apps.customUser.models import EventLog


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_request(self, request):
        # Generate a new case_id if it does not exist in the session
        if not request.session.get('case_id'):
            request.session['case_id'] = str(uuid.uuid4())

        # Record the request start time
        request.start_time = timezone.now()
        # Get the current user instance (set to None if not logged in)
        user = request.user if request.user.is_authenticated else None
        user_name = user.email if user else None  # Get the username or other fields from the custom User model

        # Get the current request's View class and `action` name
        view_class, action_name = self.get_view_class_and_action(request)
        # print(f"Processing request: View Class = {view_class}, Action = {action_name}")

        if not self.should_log(view_class):
            # print(f"Skipping logging for {view_class}")
            return

        # Use the custom `activity_name` or `action_name` as the activity name
        activity = getattr(view_class, 'activity_name', action_name)

        # Create a log record, only recording `start_time`, `end_time` is empty
        request.event_log = EventLog.objects.create(
            case_id=request.session['case_id'],
            activity=activity,
            start_time=request.start_time,
            user=user,  # Directly record the user instance
            user_name=user_name  # Record the user's name
        )
        print(f"[Event Log Created] {request.event_log}")

    def process_response(self, request, response):
        # Get the request end time
        end_time = timezone.now()

        # Ensure `event_log` was created in `process_request`
        if not hasattr(request, 'event_log'):
            return response

        # Update the `event_log` record, filling in the `end_time` field and `status_code`
        try:
            request.event_log.end_time = end_time
            request.event_log.status_code = response.status_code
            request.event_log.save()
            print(f"[Event Log Updated] {request.event_log}")
        except Exception as e:
            print(f"Error updating log in process_response: {e}")

        return response

    def get_view_class_and_action(self, request):
        """
        Get the View class and action name corresponding to the current request (e.g., the basename of a ViewSet).
        """
        try:
            resolver_match = resolve(request.path_info)
            view_func = resolver_match.func

            # Check if `view_func` is a class-based view of `viewsets` or `APIView`
            if hasattr(view_func, 'view_class'):
                view_class = view_func.view_class
                action_name = resolver_match.view_name.split('-')[-1]
            else:
                view_class = resolver_match.func.cls if hasattr(resolver_match.func, 'cls') else view_func
                action_name = view_class.__name__ if hasattr(view_class, '__name__') else str(view_class)

            # Debug information: output the resolution result
            # print(f"Resolved View Class: {view_class}, Action Name: {action_name}")
            return view_class, action_name
        except Exception as e:
            print(f"Error resolving view class and action: {e}")
            return None, None

    def should_log(self, view_class):
        """
        Check if the current View class needs to log events.
        """
        if view_class is None:
            return False
        should_log = getattr(view_class, 'log_event', False)
        # print(f"Should log for {view_class}: {should_log}")
        return should_log
