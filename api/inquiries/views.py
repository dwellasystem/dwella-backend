from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, filters
from .serializers import CreateInquirySerializer, UpdateInquirySerializer, InquiryTypeSerializer, InquirySerializer
from .models import Inquiry, InquiryType
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView


# Create your views here.

##########################################################################################
################################### Inquiry Type Views ###################################
##########################################################################################

# User model for the resident field in Inquiry model
User = get_user_model()


# Create a new inquiry type
@api_view(['POST'])
def create_inquiry_type(request):
    serializer = InquiryTypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all inquiry types
@api_view(['GET'])
def get_inquiry_types(request):
    inquiry_types = InquiryType.objects.all()
    serializer = InquiryTypeSerializer(inquiry_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get inquiry type by ID
@api_view(['GET'])
def get_inquiry_type_by_id(request, pk):
    try:
        inquiry_type = InquiryType.objects.get(pk=pk)
    except InquiryType.DoesNotExist:
        return Response({"error": "Inquiry type not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InquiryTypeSerializer(inquiry_type)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update inquiry type by ID
@api_view(['PUT'])
def update_inquiry_type_by_id(request, pk):
    try:
        inquiry_type = InquiryType.objects.get(pk=pk)
    except InquiryType.DoesNotExist:
        return Response({"error": "Inquiry type not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InquiryTypeSerializer(inquiry_type, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete inquiry type by ID
@api_view(['DELETE'])
def delete_inquiry_type_by_id(request, pk):
    try:
        inquiry_type = InquiryType.objects.get(pk=pk)
    except InquiryType.DoesNotExist:
        return Response({"error": "Inquiry type not found."}, status=status.HTTP_404_NOT_FOUND)

    inquiry_type.delete()
    return Response({'message': 'Successfully deleted inquiry type'}, status=status.HTTP_200_OK)


##########################################################################################
################################### Inquiry Views ###################################
##########################################################################################


# Create a new inquiry
@api_view(['POST'])
def create_inquiry(request):
    
    # Get the user id provided by the request 
    user_id = request.data.get('resident')

    # Check user if user id is provided and will throw error if user provided not exist. else user id is not provided set as none.
    if user_id:
        try:
            resident = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "Resident not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        resident = None

    # Check the inquiry type if exist or not throw error
    # try:
    #     inquiry_type = InquiryType.objects.get(id=request.data.get('inquiry_type'))
    # except InquiryType.DoesNotExist:
    #     return Response({"error": "Inquiry Type not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateInquirySerializer(data=request.data)
    if serializer.is_valid():
        # serializer.save(resident=resident, inquiry_type=inquiry_type)
        serializer.save(resident=resident) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all inquiries
@api_view(['GET'])
def get_inquiries(request):
    inquiries = Inquiry.objects.all()
    serializer = InquirySerializer(inquiries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get inquiry by ID
@api_view(['GET'])
def get_inquiry_by_id(request, pk):
    try:
        inquiry = Inquiry.objects.get(pk=pk)
    except Inquiry.DoesNotExist:
        return Response({"error": "Inquiry not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InquirySerializer(inquiry)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update inquiry by ID
@api_view(['PUT'])
def update_inquiry_by_id(request, pk):
    try:
        inquiry = Inquiry.objects.get(pk=pk)
    except Inquiry.DoesNotExist:
        return Response({"error": "Inquiry not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateInquirySerializer(inquiry, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete inquiry by ID
@api_view(['DELETE'])
def delete_inquiry_by_id(request, pk):
    try:
        inquiry = Inquiry.objects.get(pk=pk)
    except Inquiry.DoesNotExist:
        return Response({"error": "Inquiry not found."}, status=status.HTTP_404_NOT_FOUND)

    inquiry.delete()
    return Response({'message': 'Successfully deleted inquiry'}, status=status.HTTP_200_OK)

class PaginatedInquiries(ListAPIView):
    queryset = Inquiry.objects.all().order_by('-created_at')
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id','unit', 'resident', 'status', 'type']
    search_fields = [
        'title',
        'resident__first_name',
        'resident__last_name',
    ]
    ordering_fields = ['created_at'] # allow sorting by date and resident move-in date

######################################################################
######################## Total Counts ########################
######################################################################

#Get the total pendings
@api_view(['GET'])
def get_total_open_ionquiries(request):
    total_open = Inquiry.objects.filter(status=Inquiry.Status.OPEN).count()
    return Response({"open": total_open})