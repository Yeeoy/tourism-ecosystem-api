from rest_framework import viewsets


class LoggingViewSet(viewsets.ModelViewSet):
    log_event = True
    activity_name = "Default Activity"

    def get_activity_name(self, action_name=None):
        """
        Returns the activity name based on the class and the action name.
        If no action_name is passed, it uses self.action.
        """
        if not action_name and hasattr(self, 'action'):
            action_name = self.action

        # Use the class name if activity_name is not set
        base_name = self.activity_name if self.activity_name != "Default Activity" else self.__class__.__name__.replace(
            'ViewSet', '')

        # Map action names to more readable formats
        action_mapping = {
            'list': 'List',
            'create': 'Create',
            'retrieve': 'Retrieve',
            'update': 'Update',
            'partial_update': 'Partial Update',
            'destroy': 'Delete'
        }

        # Use the mapped action name if available, otherwise capitalize the action name
        action_display = action_mapping.get(action_name, action_name.capitalize())

        # Capitalize the action name and append it to the base_name
        return f"{base_name} {action_display}"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to ensure request, args, and kwargs are set and super dispatch is called.
        """
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return super().dispatch(request, *args, **kwargs)
