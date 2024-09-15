# 导入需要创建数据的模型和自定义用户模型
import os

import django
# 使用 get_user_model 获取自定义的 User 模型
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.local_attractions_museums.models import (Attraction, Booking,
                                                   EducationContent,
                                                   Museum, Ticket, TourGuide)

# 设置 Django 环境变量，确保指向正确的 settings 模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tourism_ecosystem.settings")

# 初始化 Django
django.setup()

User = get_user_model()  # 获取自定义的 User 模型


def create_test_LAM_data():
    # 创建一些 Museum 数据，提供 ticket_price 值
    museum1 = Museum.objects.create(
        name="Art Museum",
        description="An art museum with a variety of historical paintings.",
        location="City Center",
        opening_hours="9 AM",
        closing_hours="5 PM",
        is_open=True,
        ticket_price=20.00  # 提供 ticket_price
    )

    museum2 = Museum.objects.create(
        name="History Museum",
        description="Museum showcasing historical artifacts.",
        location="Old Town",
        opening_hours="10 AM",
        closing_hours="6 PM",
        is_open=True,
        ticket_price=15.00  # 提供 ticket_price
    )

    # 创建一些 Attraction 数据，提供 ticket_price 值
    attraction1 = Attraction.objects.create(
        name="Medieval Castle",
        description="A grand castle from the medieval era.",
        location="Hilltop",
        opening_hours="9 AM",
        closing_hours="5 PM",
        is_open=True,
        ticket_price=30.00  # 提供 ticket_price
    )

    attraction2 = Attraction.objects.create(
        name="Ancient Ruins",
        description="Remains of an ancient civilization.",
        location="Valley",
        opening_hours="8 AM",
        closing_hours="6 PM",
        is_open=True,
        ticket_price=25.00  # 提供 ticket_price
    )

    # 创建一些 TourGuide 数据
    guide1 = TourGuide.objects.create(
        name="John Doe",
        bio="Experienced guide with a passion for history.",
        available_from="09:00",
        available_to="17:00",
        languages="English, French"
    )

    guide2 = TourGuide.objects.create(
        name="Jane Smith",
        bio="Specialized in art tours.",
        available_from="10:00",
        available_to="18:00",
        languages="English, Spanish"
    )

    # 创建一些 Ticket 数据，确保提供 price 值
    ticket1 = Ticket.objects.create(
        attraction=attraction1,
        museum=museum1,
        price=25.00,  # 提供 price 字段的值
        purchase_date=timezone.now(),
        valid_until=timezone.now() + timezone.timedelta(days=30)
    )

    ticket2 = Ticket.objects.create(
        attraction=attraction2,
        museum=museum2,
        price=15.00,  # 提供 price 字段的值
        purchase_date=timezone.now(),
        valid_until=timezone.now() + timezone.timedelta(days=60)
    )

    # 创建用户，使用 email 代替 username
    user, created = User.objects.get_or_create(
        email="testuser@example.com",
        defaults={
            "name": "Test User",
            "password": "testpass123"
        }
    )

    # 创建一些 Booking 数据
    booking1 = Booking.objects.create(
        user=user,
        ticket=ticket1,
        guide=guide1,
        booking_date=timezone.now(),
        visit_date=timezone.now() + timezone.timedelta(days=7)
    )
    print(booking1)

    booking2 = Booking.objects.create(
        user=user,
        ticket=ticket2,
        guide=guide2,
        booking_date=timezone.now(),
        visit_date=timezone.now() + timezone.timedelta(days=14)
    )
    print(booking2)

    # 创建一些 EducationContent 数据
    edu_content1 = EducationContent.objects.create(
        title="Introduction to Renaissance Art",
        description="A comprehensive guide to Renaissance art.",
        related_museum=museum1,
        related_attraction=attraction1,
        content_url="http://example.com/renaissance-art"
    )
    print(edu_content1)

    edu_content2 = EducationContent.objects.create(
        title="Medieval History",
        description="Learn about the medieval era and its importance.",
        related_museum=museum2,
        related_attraction=attraction2,
        content_url="http://example.com/medieval-history"
    )
    print(edu_content2)

    print("Test data created successfully!")


def create_test_data():
    create_test_LAM_data()


# 调用函数创建测试数据
if __name__ == "__main__":
    create_test_data()
