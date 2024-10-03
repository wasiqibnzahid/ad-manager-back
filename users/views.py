from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from .serializers import NormalUserSerializer, NormalUserProfileSerializer, ReportSerializer, RecordSerializer
from rest_framework.permissions import IsAdminUser
from datetime import datetime
from .models import Report, Record
from .create_report import process_report, fetch_ad_units
from threading import Thread
from .models import NormalUserProfile
from django.contrib.auth.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):

    response = {
        'username': request.user.username,
        'email': request.user.email,
        'is_admin': request.user.is_superuser,
    }
    if (response["is_admin"] == False):
        print(f"RARARA, {request.user}")
        normaluser = NormalUserProfile.objects.get(user_id=request.user.id)
        report_id = normaluser.report_id
        response["report_id"] = report_id
    user_data = response
    return Response(user_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    data = request.data
    data["report_id"] = data.get("report_id", None)
    data["is_admin"] = data.get("is_admin", False)
    if (data["is_admin"]):
        user = User.objects.create_superuser(
            username=data["username"], password=data["password"])
        NormalUserProfile.objects.create(user=user)
        return Response({"status": "success"})
    serializer = NormalUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_user(request):
    data = request.data
    data["is_admin"] = data.get("is_admin", False)
    user = NormalUserProfile.objects.get(pk=data["id"])
    
    if (user):
        user.report_id = data["report_id"]
        if(data["is_admin"]):
            user.report_id = None
        user.save()
        user = user.user
        user.is_staff = data["is_admin"]
        user.is_admin = data["is_admin"]
        user.is_superuser = data["is_admin"]
        user.username = data["username"]
        if (data['password']):
            user.set_password(data["password"])
        user.save()
        return Response({'message': 'User updated successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_report(request):

    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')

    ad_unit_ids = request.data.get('ad_unit_ids')
    name = request.data.get('name')
    cpm_rate = float(request.data.get('cpm'))
    print(f"ASDASD {start_date_str}")

    if not all([start_date_str, end_date_str, ad_unit_ids, cpm_rate]):
        return Response({'error': 'All fields (report_id, start_date, end_date, ad_unit_ids, cpm_rate) are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = datetime.strptime(
            start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        end_date = datetime.strptime(
            end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    report = Report.objects.create(
        start_date=start_date,
        end_date=end_date,
        ad_unit_ids=','.join(map(str, ad_unit_ids)),
        cpm_rate=cpm_rate,
        status='Processing',
        name=name
    )

    report_thread = Thread(target=process_report, args=(
        report.pk, start_date, end_date, ad_unit_ids, cpm_rate))
    report_thread.start()

    return Response({'message': 'Report created successfully!', 'report_id': report.pk}, status=status.HTTP_201_CREATED)


ad_units = fetch_ad_units()


@api_view(["GET"])
def get_ad_units(request):
    return Response(ad_units)


@api_view(["GET"])
def list_users(request):
    users = NormalUserProfile.objects.all()
    serializer = NormalUserProfileSerializer(
        users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_reports(request):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_report(request, report_id):
    ReportData = Report.objects.get(pk=report_id)
    Record.objects.filter(report_id=ReportData.pk).delete()
    ReportData.delete()

    return Response({"status": "200"})


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    NormalUser = NormalUserProfile.objects.get(pk=user_id)
    NormalUser.user.delete()
    NormalUser.delete()

    return Response({"status": "200"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_records(request, report_id):
    try:
        records = Record.objects.filter(report_id=report_id)
        serialized = RecordSerializer(
            records,
            many=True
        )
        return Response(serialized.data)
    except:
        return Response([])


@api_view(["POST"])
@permission_classes([IsAdminUser])
def assign_report(request):
    data = request.data
    user_id = data.get('user_id', None)
    normalUser = NormalUserProfile.objects.get(pk=user_id)
    normalUser.report_id = data.get("report_id", None)
    normalUser.save()
    return Response({"status": "success"})
