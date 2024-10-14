import logging
from io import BytesIO

import pandas as pd
from django.http import JsonResponse, HttpResponse
from drf_spectacular.utils import extend_schema
# 导入 PM4PY 相关库
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from apps.customUser.serializers import (
    UserSerializer,
    AuthTokenSerializer, EventLogSerializer
)
from .models import EventLog


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    log_event = True
    activity_name = "User Registration"


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    log_event = True
    activity_name = "User Authentication"

    def post(self, request, *args, **kwargs):
        # Validate and authenticate the user
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Create or retrieve the authentication token for the user
        token, created = Token.objects.get_or_create(user=user)

        # Return response with token and user_id
        return Response({
            'token': token.key,
            'user_id': user.id,
        })


# A generic view class for handling GET and PUT requests, allowing the retrieval and update of objects
@extend_schema(tags=['User'])
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    log_event = True
    activity_name = "User Profile Management"

    def get_object(self):
        return self.request.user


# Create or configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class EventLogPagination(PageNumberPagination):
    page_size = 10  # 每页默认 10 条记录
    page_size_query_param = 'page_size'  # 允许前端通过查询参数自定义每页条数
    max_page_size = 100  # 限制每页最多 100 条记录


@extend_schema(tags=['Event Log'])
class EventLogListView(generics.ListAPIView):
    queryset = EventLog.objects.all().order_by('-start_time')
    serializer_class = EventLogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = EventLogPagination


@extend_schema(tags=['Event Log'])
class GenerateAndDownloadCSV(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        try:
            # 第一步：从数据库中检索所有用户事件日志数据
            events = EventLog.objects.all().values('case_id', 'activity', 'start_time', 'end_time', 'user_id', 'user',
                                                   'user_name')
            df = pd.DataFrame(list(events))

            if df.empty:
                logging.error("No events found in the database.")
                return JsonResponse({"message": "No events found."}, status=404)

            # 修改列名为大写或你需要的格式
            df.columns = ['Case_id', 'Activity', 'Start_time', 'End_time', 'User_id', 'User', 'User_name']

            # 格式化日期列，格式为 "日.月.年 时:分"
            df['Start_time'] = pd.to_datetime(df['Start_time']).dt.strftime('%-d.%-m.%y %H:%M')
            df['End_time'] = pd.to_datetime(df['End_time']).dt.strftime('%-d.%-m.%y %H:%M')

            # 重命名列名为你需要的格式
            df.rename(columns={
                'Start_time': 'Start Date',
                'End_time': 'End Date'
            }, inplace=True)

            # 第二步：检查数据格式并准备 CSV 数据
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)  # 重置指针到开始位置

            logging.info("Successfully created CSV file in memory.")

            # 第三步：提供文件给用户下载
            response = HttpResponse(csv_buffer.getvalue(), content_type='application/csv')
            response['Content-Disposition'] = 'attachment; filename="event_log.csv"'
            return response

        except Exception as e:
            # 输出详细的错误日志
            logging.error(f"An error occurred during CSV generation or download: {e}")
            return JsonResponse({"message": f"Internal Server Error: {e}"}, status=500)


@extend_schema(tags=['Event Log'])
class ClearEventLogView(APIView):
    """
    API View to clear all event logs from the database.
    Only accessible to admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        # Clear all EventLog data
        deleted, _ = EventLog.objects.all().delete()

        # Return response
        return Response({"message": f"Successfully deleted {deleted} event logs."}, status=status.HTTP_200_OK)


@extend_schema(tags=['Event Log'])
class GenerateAndDownloadXES(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        try:
            events = EventLog.objects.all().values(
                'case_id', 'activity', 'start_time', 'end_time', 'user_id', 'user_name', 'status_code'
            )
            df = pd.DataFrame(list(events))

            if df.empty:
                logging.error("没有找到事件日志。")
                return JsonResponse({"message": "没有找到事件日志。"}, status=404)

            # 重命名列以符合 PM4PY 的要求
            df.rename(columns={
                'case_id': 'case:concept:name',
                'activity': 'concept:name',
                'start_time': 'time:timestamp',
                'end_time': 'time:endTimestamp',
                'user_name': 'org:resource',
                'status_code': 'status'
            }, inplace=True)

            # 确保时间戳列的格式正确（ISO 8601）
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            df['time:endTimestamp'] = pd.to_datetime(df['time:endTimestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

            # 添加生命周期信息
            df['lifecycle:transition'] = 'complete'

            # 按照 case_id 和 timestamp 排序
            df = df.sort_values(['case:concept:name', 'time:timestamp'])

            # 将 DataFrame 转换为 event log 对象
            event_log = log_converter.apply(df)

            # 创建一个内存文件对象来存储 XES 文件
            xes_buffer = BytesIO()

            # 将 event log 导出为 XES 格式
            xes_exporter.apply(event_log, xes_buffer)
            xes_buffer.seek(0)  # 重置指针到开始位置

            logging.info("成功创建 XES 文件。")

            # 提供文件给用户下载
            response = HttpResponse(xes_buffer.getvalue(), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename="event_log.xes"'
            return response

        except Exception as e:
            logging.error(f"生成或下载 XES 文件时发生错误: {e}")
            return JsonResponse({"message": f"内部服务器错误: {e}"}, status=500)
