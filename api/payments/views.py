from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, filters
from django.contrib.auth import get_user_model
from .serializers import CreatePaymentSerializer, CreatePaymentMethodSerializer, GetPaymentSerializer
from .models import PaymentRecord, PaymentMethod
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from units.models import Unit, AssignedUnit
User = get_user_model()

# Create your views here.

######################################################################
######################## Payment Method Views ########################
######################################################################


# Create a payment method
@api_view(['POST'])
def create_payment_method(request):
    serializer = CreatePaymentMethodSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all payment methods
@api_view(['GET'])
def get_payment_methods(request):
    payment_methods = PaymentMethod.objects.all()
    serializer = CreatePaymentMethodSerializer(payment_methods, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get payment method by ID
@api_view(['GET'])
def get_payment_method_by_id(request, pk):
    try:
        payment_method = PaymentMethod.objects.get(pk=pk)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Payment method not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CreatePaymentMethodSerializer(payment_method)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update payment method by ID
@api_view(['PUT'])
def update_payment_method_by_id(request, pk):   
    try:
        payment_method = PaymentMethod.objects.get(pk=pk)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Payment method not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreatePaymentMethodSerializer(payment_method, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete payment method by ID
@api_view(['DELETE'])
def delete_payment_method_by_id(request, pk):
    try:
        payment_method = PaymentMethod.objects.get(pk=pk)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Payment method not found."}, status=status.HTTP_404_NOT_FOUND)
    
    payment_method.delete()
    return Response({'message': 'Successfully deleted payment method'}, status=status.HTTP_200_OK)


######################################################################
######################## Payment Record Views ########################
######################################################################


# Create a payment record
@api_view(['POST'])
def create_payment(request):
    user_id = request.data.get('user')
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = CreatePaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save()

        # If this is a completed advance payment, allocate it to future bills
        if (payment.payment_type == PaymentRecord.PaymentType.ADVANCE and 
            payment.status == PaymentRecord.PaymentStatus.COMPLETED):
            bills_created = payment.allocate_advance_payment()

            return Response({
                **serializer.data,
                'advance_allocation': f'Created {bills_created} advance bills'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all payment records
@api_view(['GET'])
def get_payments(request):
    payments = PaymentRecord.objects.all()
    serializer = GetPaymentSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get payment record by ID
@api_view(['GET'])
def get_payment_by_id(request, pk):
    try:
        payment = PaymentRecord.objects.get(pk=pk)
    except PaymentRecord.DoesNotExist:
        return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GetPaymentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update payment record by ID
@api_view(['PUT'])
def update_payment_by_id(request, pk):
    try:
        payment = PaymentRecord.objects.get(pk=pk)
    except PaymentRecord.DoesNotExist:
        return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreatePaymentSerializer(payment, data=request.data, partial=True)
    if serializer.is_valid():
        updated_payment = serializer.save()

        # ✅ If payment is updated to "paid", update the linked bill too
        if updated_payment.status == PaymentRecord.PaymentStatus.COMPLETED:
            # Make sure this payment has an associated bill
            if hasattr(updated_payment, 'bill') and updated_payment.bill:
                bill = updated_payment.bill
                bill.payment_status = bill.PaymentStatus.PAID
                bill.update_due_status()  # also updates due_status to DONE
                bill.save()
            
            # For advance payments, allocate to future bills
            if (updated_payment.payment_type == PaymentRecord.PaymentType.ADVANCE and 
                not updated_payment.is_advance_allocated):
                bills_created = updated_payment.allocate_advance_payment()
                
                return Response({
                    **serializer.data,
                    'advance_allocation': f'Created {bills_created} advance bills'
                }, status=status.HTTP_200_OK)
            
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def calculate_advance_payment(request):
    """
    Calculate the total amount for advance payment based on date range
    """
    user_id = request.data.get('user')
    unit_id = request.data.get('unit')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    try:
        user = User.objects.get(pk=user_id)
        unit = Unit.objects.get(pk=unit_id)
        
        # Validate dates
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start >= end:
            return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate number of months
        from dateutil.relativedelta import relativedelta
        months = 0
        current = start
        while current <= end:
            months += 1
            current = current + relativedelta(months=1)
        
        # Calculate monthly amount
        monthly_rent = float(unit.rent_amount)
        additional_charges = 0
        
        try:
            assigned_unit = AssignedUnit.objects.get(
                unit_id=unit, 
                assigned_by=user, 
                deleted_at__isnull=True
            )
            if assigned_unit.amenities:
                additional_charges += 2500
            if assigned_unit.security:
                additional_charges += 2000
            if assigned_unit.maintenance:
                additional_charges += 1500
        except AssignedUnit.DoesNotExist:
            pass
        
        total_monthly = monthly_rent + additional_charges
        total_amount = total_monthly * months
        
        return Response({
            'user': user_id,
            'unit': unit_id,
            'start_date': start_date,
            'end_date': end_date,
            'months_covered': months,
            'monthly_amount': total_monthly,
            'total_amount': total_amount,
            'breakdown': {
                'base_rent': monthly_rent,
                'additional_charges': additional_charges,
                'months': months
            }
        })
        
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Unit.DoesNotExist:
        return Response({"error": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Delete payment record by ID
@api_view(['DELETE'])
def delete_payment_by_id(request, pk):
    try:
        payment = PaymentRecord.objects.get(pk=pk)
    except PaymentRecord.DoesNotExist:
        return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
    
    payment.delete()
    return Response({'message': 'Successfull deleted payment'}, status=status.HTTP_200_OK)


class PaginatedPayments(ListAPIView):
    queryset = PaymentRecord.objects.all().order_by('-created_at')
    serializer_class = GetPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id','user', 'amount', 'status', 'payment_method', 'unit', 'payment_type']
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__middle_name',
        'user__email',
        'reference_number',
        'payment_method__name',
        'unit__unit_name',
        'status',
        'payment_date',
        'payment_type'
    ]
    ordering_fields = ['amount', 'created_at', 'bill__due_date', 'advance_start_date'] # allow sorting by amount and date
    ordering = ['-advance_start_date', '-bill__due_date']  # default order


######################################################################
######################## Total Counts ################################
######################################################################

#Get the total pendings
@api_view(['GET'])
def get_total_pendings(request):
    total_pendings = PaymentRecord.objects.filter(status=PaymentRecord.PaymentStatus.PENDING).count()
    return Response({"pending": total_pendings})


######################################################################
######################## Advance Payment #############################
######################################################################


@api_view(['POST'])
def calculate_advance_payment(request):
    """
    Calculate the total amount for advance payment based on date range
    """
    user_id = request.data.get('user')
    unit_id = request.data.get('unit')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    try:
        user = User.objects.get(pk=user_id)
        unit = Unit.objects.get(pk=unit_id)
        
        # Validate dates
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start >= end:
            return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate number of months
        from dateutil.relativedelta import relativedelta
        months = 0
        current = start
        while current <= end:
            months += 1
            current = current + relativedelta(months=1)
        
        # Calculate monthly amount
        monthly_rent = float(unit.rent_amount)
        additional_charges = 0
        
        try:
            assigned_unit = AssignedUnit.objects.get(
                unit_id=unit, 
                assigned_by=user, 
                deleted_at__isnull=True
            )
            if assigned_unit.amenities:
                additional_charges += 2500
            if assigned_unit.security:
                additional_charges += 2000
            if assigned_unit.maintenance:
                additional_charges += 1500
        except AssignedUnit.DoesNotExist:
            pass
        
        total_monthly = monthly_rent + additional_charges
        total_amount = total_monthly * months
        
        return Response({
            'user': user_id,
            'unit': unit_id,
            'start_date': start_date,
            'end_date': end_date,
            'months_covered': months,
            'monthly_amount': total_monthly,
            'total_amount': total_amount,
            'breakdown': {
                'base_rent': monthly_rent,
                'additional_charges': additional_charges,
                'months': months
            }
        })
        
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Unit.DoesNotExist:
        return Response({"error": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

api_view(['GET'])
def get_advance_payments(request, user_id):
    """
    Get all advance payments for a specific user
    """
    try:
        user = User.objects.get(pk=user_id)
        advance_payments = PaymentRecord.objects.filter(
            user=user,
            payment_type=PaymentRecord.PaymentType.ADVANCE
        ).order_by('-created_at')
        
        serializer = GetPaymentSerializer(advance_payments, many=True)
        return Response(serializer.data)
    
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)