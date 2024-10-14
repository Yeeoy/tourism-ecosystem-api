import logging
import uuid

from django.urls import resolve
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ViewSet, ModelViewSet

from apps.customUser.models import EventLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            self.process_request(request)
            response = self.get_response(request)
            self.process_response(request, response)
            return response
        except Exception as e:
            logger.error(f"Unexpected error in RequestLoggingMiddleware: {str(e)}")
            return self.get_response(request)

    def process_request(self, request):
        try:
            user = self.get_user_from_token(request)
            case_id = self.get_or_create_case_id(request, user)
            request.session['case_id'] = case_id

            request.start_time = timezone.now()
            user_name = getattr(user, 'email', 'Anonymous')
            user_id = user.id if user else None

            view_class, action_name = self.get_view_class_and_action(request)
            logger.debug(f"View class: {view_class}, Action name: {action_name}")

            if view_class:
                if hasattr(view_class, 'get_activity_name'):
                    activity = view_class.get_activity_name(action_name)
                elif hasattr(view_class, 'activity_name'):
                    activity = f"{view_class.activity_name} {action_name.capitalize()}"
                else:
                    activity = f"{view_class.__name__.replace('ViewSet', '')} {action_name.capitalize()}"
            else:
                activity = f"Unknown Activity {action_name.capitalize()}"

            logger.debug(f"Generated activity name: {activity}")

            request.event_log = EventLog.objects.create(
                case_id=case_id,
                activity=activity,
                start_time=request.start_time,
                user_id=user_id,
                user_name=user_name
            )
            logger.info(f"[Event Log Created] {request.event_log}")
            logger.debug(f"Event Log ID: {request.event_log.id}, Start Time: {request.event_log.start_time}")
        except Exception as e:
            logger.error(f"Error in process_request: {str(e)}")

    def get_user_from_token(self, request):
        """
        从请求中的Token获取用户
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                return token.user
            except Token.DoesNotExist:
                pass
        return None

    def process_response(self, request, response):
        try:
            if hasattr(request, 'event_log'):
                end_time = timezone.now()
                request.event_log.end_time = end_time
                request.event_log.status_code = response.status_code
                request.event_log.save()
                logger.info(f"[Event Log Updated] {request.event_log}")

                if self.is_process_completed(request, response):
                    request.session.pop('case_id', None)
            else:
                logger.warning("No event_log found on request object")
        except Exception as e:
            logger.error(f"Error in process_response: {str(e)}")
        finally:
            return response

    def get_view_class_and_action(self, request):
        """
        解析请求中的视图类和动作。
        """
        try:
            resolver_match = resolve(request.path_info)
            view_func = resolver_match.func
            view_class = None
            action_name = None

            if hasattr(view_func, 'view_class'):
                view_class = view_func.view_class
                view_instance = view_class()

                # 尝试确定action
                if hasattr(view_instance, 'action_map'):
                    action_name = view_instance.action_map.get(request.method.lower())

                if not action_name and (issubclass(view_class, ViewSet) or issubclass(view_class, ModelViewSet)):
                    # 对于ViewSet和ModelViewSet，我们可以根据HTTP方法和URL模式推断action
                    if 'pk' in resolver_match.kwargs:
                        action_map = {
                            'get': 'retrieve',
                            'put': 'update',
                            'patch': 'partial_update',
                            'delete': 'destroy'
                        }
                    else:
                        action_map = {
                            'get': 'list',
                            'post': 'create'
                        }
                    action_name = action_map.get(request.method.lower())

                if not action_name:
                    action_name = resolver_match.url_name.split('-')[-1]
            elif hasattr(view_func, '__name__'):
                view_class = view_func
                action_name = view_func.__name__

            if not action_name:
                action_name = request.method.lower()

            return view_class, action_name
        except Exception as e:
            logger.error(f"Error resolving view class and action: {str(e)}")
            return None, 'unknown'

    def should_log(self, view_class):
        """
        Determines whether the view class should log an event.
        """
        if view_class is None:
            return False
        return getattr(view_class, 'log_event', False)

    def get_or_create_case_id(self, request, user):
        """
        生成或获取用于日志记录的case ID。
        """
        try:
            if user:
                return f"user_{user.id}"
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                return f"session_{session_key}"
        except Exception as e:
            logger.error(f"Error in get_or_create_case_id: {str(e)}")
            return f"error_{uuid.uuid4().hex}"

    def is_process_completed(self, request, response):
        """
        Determines if the process is completed based on response.
        """
        try:
            view_class, action_name = self.get_view_class_and_action(request)
            if action_name == 'logout':
                return True
            if response.status_code >= 400:
                return True
            return False
        except Exception as e:
            logger.error(f"Error in is_process_completed: {str(e)}")
            return False
