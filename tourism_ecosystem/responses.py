from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import exception_handler


class CustomResponse:
    """
    Custom response class to encapsulate a unified response format
    """

    @staticmethod
    def success(data=None, msg="Operation successful", code=200):
        """
        Success response
        :param data: Response data
        :param msg: Message
        :param code: Status code, default is 200
        :return: Formatted Response
        """
        return Response({
            "code": code,
            "msg": msg,
            "data": data
        }, status=code)

    @staticmethod
    def error(msg="Request error", code=400):
        """
        Error response
        :param msg: Error message
        :param code: Status code, default is 400
        :return: Formatted Response
        """
        return Response({
            "code": code,
            "msg": msg,
            "data": None
        }, status=code)


class CustomRenderer(JSONRenderer):
    """
    Custom renderer class to encapsulate a unified JSON response format
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Check if the data is already in custom format
        if isinstance(data, dict) and 'code' in data and 'msg' in data:
            return super(CustomRenderer, self).render(data, accepted_media_type, renderer_context)

        # If it is an error response, keep it as is (handled by the exception handler)
        response = renderer_context['response']
        if response.status_code >= 400:
            return super(CustomRenderer, self).render(data, accepted_media_type, renderer_context)

        # Encapsulate successful response data
        response_data = {
            'code': response.status_code,
            'msg': 'success',
            'data': data
        }

        return super(CustomRenderer, self).render(response_data, accepted_media_type, renderer_context)


def custom_exception_handler(exc, context):
    # Call the default DRF exception handler
    response = exception_handler(exc, context)

    if response is not None:
        # print(f"Error detail: {response.data}")  # Print detailed error information
        # Extract error information and construct custom response
        code = response.status_code
        # msg = response.data.get('detail', 'request error')
        msg = response.data
        return CustomResponse.error(msg=msg, code=code)
    else:
        return response
