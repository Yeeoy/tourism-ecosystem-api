from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import exception_handler


class CustomResponse:
    """
    自定义响应类，封装统一的响应格式
    """

    @staticmethod
    def success(data=None, msg="操作成功", code=200):
        """
        成功响应
        :param data: 响应数据
        :param msg: 提示信息
        :param code: 状态码，默认为 200
        :return: 格式化后的 Response
        """
        return Response({
            "code": code,
            "msg": msg,
            "data": data
        }, status=code)

    @staticmethod
    def error(msg="请求错误", code=400):
        """
        错误响应
        :param msg: 错误提示信息
        :param code: 状态码，默认为 400
        :return: 格式化后的 Response
        """
        return Response({
            "code": code,
            "msg": msg,
            "data": None
        }, status=code)


class CustomRenderer(JSONRenderer):
    """
    自定义渲染器类，统一封装成功的 JSON 响应格式
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # 检查数据是否已经是自定义格式
        if isinstance(data, dict) and 'code' in data and 'msg' in data:
            return (super(CustomRenderer, self)
                    .render(data, accepted_media_type, renderer_context))

        # 如果是错误响应，保持现状（异常处理器已经处理）
        response = renderer_context['response']
        if response.status_code >= 400:
            return super(CustomRenderer, self).render(data, accepted_media_type, renderer_context)

        # 统一封装成功的响应数据
        response_data = {
            'code': response.status_code,
            'msg': 'success',
            'data': data
        }

        return super(CustomRenderer, self.render(response_data, accepted_media_type, renderer_context))


def custom_exception_handler(exc, context):
    # 调用默认的 DRF 异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 提取错误信息，构建自定义响应
        code = response.status_code
        msg = response.data.get('detail', 'request error')
        return CustomResponse.error(msg=msg, code=code)
    else:
        return response
