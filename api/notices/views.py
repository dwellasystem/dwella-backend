from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, filters
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from .serializers import CreateNoticeSerializer, NoticeTypeSerializer, NoticeSerializer, UpdateCreateNoticeSerializer
from .models import Notice, NoticeType
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q


# Create your views here.


######################## Notice Type Views ########################


# Create a new notice type
@api_view(['POST'])
def create_notice_type(request):
    serializer = NoticeTypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all notice types
@api_view(['GET'])
def get_notice_types(request):
    notice_types = NoticeType.objects.all()
    serializer = NoticeTypeSerializer(notice_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get notice type by ID
@api_view(['GET'])
def get_notice_type_by_id(request, pk):
    try:
        notice_type = NoticeType.objects.get(pk=pk)
    except NoticeType.DoesNotExist:
        return Response({"error": "Notice type not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = NoticeTypeSerializer(notice_type)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update notice type by ID
@api_view(['PUT'])
def update_notice_type_by_id(request, pk):
    try:
        notice_type = NoticeType.objects.get(pk=pk)
    except NoticeType.DoesNotExist:
        return Response({"error": "Notice type not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = NoticeTypeSerializer(notice_type, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete notice type by ID
@api_view(['DELETE'])
def delete_notice_type(request, pk):
    try:
        notice_type = NoticeType.objects.get(pk=pk)
    except NoticeType.DoesNotExist:
        return Response({"error": "Notice type not found."}, status=status.HTTP_404_NOT_FOUND)
    
    notice_type.delete()
    return Response({'message': 'Successfully deleted notice type'}, status=status.HTTP_200_OK)


######################## Notices Views ########################


@api_view(['POST'])
def create_notice(request):
    serializer = CreateNoticeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all notices
@api_view(['GET'])
def get_notices(request):
    notices = Notice.objects.all()
    serializer = NoticeSerializer(notices, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get notice by ID
@api_view(['GET'])
def get_notice_by_id(request, pk):
    try:
        notice = Notice.objects.get(pk=pk)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = NoticeSerializer(notice)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update notice by ID
@api_view(['PUT'])
def update_notice_by_id(request, pk):
    try:
        notice = Notice.objects.get(pk=pk)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UpdateCreateNoticeSerializer(notice, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete notice by ID
@api_view(['DELETE'])
def delete_notice(request, pk):
    try:
        notice = Notice.objects.get(pk=pk)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found."}, status=status.HTTP_404_NOT_FOUND)
    
    notice.delete()
    return Response({'message': 'Successfully deleted notice'}, status=status.HTTP_200_OK)


class PaginatedNotices(ListAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'content', 'notice_type', 'target_audience', 'target_audience__assigned_by']
    search_fields = [
        'title',
        'content'
    ]

    def get_queryset(self):
        qs = Notice.objects.all().order_by('-created_at')
        unit_id = self.request.query_params.get("target_audience")  # 👈 get unit from URL

        if unit_id:
            qs = qs.filter(Q(target_audience__isnull=True) | Q(target_audience=unit_id)).distinct()

        return qs
