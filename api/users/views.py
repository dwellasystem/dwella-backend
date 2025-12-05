from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import ExtractMonth, ExtractYear
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from django.db.models import Count
import calendar


from .models import CustomUser
from .serializers import (
    RegisterSerializer, 
    UpdateUserSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)

# Register/Create User
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'message':'Successfully registered', 'data':serializer.data['id']}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get All Users
class UserListView(ListAPIView):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']
    pagination_class = None


# Get User by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update User by ID
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_by_id(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = UpdateUserSerializer(user, data=request.data, context={'updated_by': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Delete User by ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_by_id(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.soft_delete(by_user=request.user)
    return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_deleted_user(request, pk):
    try:
        user = CustomUser.all_objects.get(pk=pk)
        user.restore()
        return Response({'message': 'User restored successfully.'})
    except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    

class PaginatedUsers(ListAPIView):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'move_in_date', 'first_name', 'last_name', 'account_status']
    search_fields = ['first_name', 'last_name', 'email', 'username']



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # change to AllowAny if public
def user_summary_stats(request):
    """
    Returns total users, total active, and total inactive users.
    Example:
    {
        "totalUsers": 45,
        "totalActiveResidents": 30,
        "totalInactiveResidents": 15,
        "totalActiveEmployees: 20,
        "totalInactiveEmployees: 3
    }
    """
    total_users = CustomUser.objects.count()
    total_active_residents = CustomUser.objects.filter(account_status='active', role='resident').count()
    total_inactive_residents = CustomUser.objects.filter(account_status='inactive', role='resident').count()
    total_active_employees = CustomUser.objects.filter(account_status='active', role='employee').count()
    total_inactive_employees = CustomUser.objects.filter(account_status='inactive', role='employee').count()
    

    data = {
        "totalUsers": total_users,
        "totalActiveResidents": total_active_residents,
        "totalInactiveResidents": total_inactive_residents,
        "totalActiveEmployees": total_active_employees,
        "totalInactiveEmployees": total_inactive_employees
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats_monthly(request):
    users_per_month = (
        CustomUser.objects.filter(role="resident")
        .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at'))
        .values('year', 'month')
        .annotate(numberOfUsers=Count('id'))
        .order_by('year', 'month')
    )

    # Convert month number (1-12) to month name
    formatted_data = [
        {
            "year": item["year"],
            "month": calendar.month_name[item["month"]],
            "numberOfUsers": item["numberOfUsers"]
        }
        for item in users_per_month
    ]

    return Response(formatted_data, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


# Password Reset Views
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{reset_token}/"
            
            # Send email with beautiful HTML formatting
            subject = "Reset Your Dwella Password"
            
            # Beautiful HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #344CB7, #2a3da0);
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .header h1 {{
                        color: white;
                        margin: 0;
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .content {{
                        background: #ffffff;
                        padding: 30px;
                        border: 1px solid #e0e0e0;
                        border-top: none;
                        border-radius: 0 0 10px 10px;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #344CB7, #2a3da0);
                        color: white !important;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 16px;
                        margin: 20px 0;
                        text-align: center;
                        box-shadow: 0 4px 15px rgba(52, 76, 183, 0.3);
                        transition: all 0.3s ease;
                    }}
                    .button:hover {{
                        background: linear-gradient(135deg, #2a3da0, #1e2d7a);
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(52, 76, 183, 0.4);
                    }}
                    .reset-link {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        word-break: break-all;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e0e0e0;
                        color: #666;
                        font-size: 12px;
                    }}
                    .user-name {{
                        color: #344CB7;
                        font-weight: bold;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        color: #856404;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔐 Dwella</h1>
                </div>
                
                <div class="content">
                    <h2>Password Reset Request</h2>
                    
                    <p>Hello <span class="user-name">{user.first_name or user.username}</span>,</p>
                    
                    <p>We received a request to reset your password for your Dwella account. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Your Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    
                    <div class="reset-link">
                        {reset_link}
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in 24 hours for security reasons.
                    </div>
                    
                    <p>If you didn't request this password reset, please ignore this email. Your account remains secure.</p>
                    
                    <p>Need help? Contact our support team or reply to this email.</p>
                </div>
                
                <div class="footer">
                    <p>© 2024 Dwella. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            plain_message = f"""
            Password Reset Request - Dwella
            
            Hello {user.first_name or user.username},
            
            You requested a password reset for your Dwella account.
            
            Please click the link below to reset your password:
            {reset_link}
            
            This link will expire in 24 hours.
            
            If you didn't request this reset, please ignore this email.
            
            Need help? Contact our support team.
            
            Best regards,
            Dwella Team
            
            © 2024 Dwella. All rights reserved.
            """
            
            print(f"📧 Password reset link for {email}: {reset_link}")
            
            # Send email
            try:
                from django.core.mail import EmailMultiAlternatives
                import sendgrid
                from sendgrid.helpers.mail import Mail, Content, To, From
                
                # email_msg = EmailMultiAlternatives(
                #     subject=subject,
                #     body=plain_message,
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     to=[user.email],
                # )
                # email_msg.attach_alternative(html_message, "text/html")
                # email_msg.send()

                                # Initialize SendGrid client
                sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                
                # Create email
                from_email = From(settings.DEFAULT_FROM_EMAIL)
                to_email = To(user.email)
                subject = "Reset Your Dwella Password"
                
                # Create mail object
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_message,
                    plain_text_content=plain_message
                )
                
                # Send email
                response = sg.client.mail.send.post(request_body=mail.get())
                
                print(f"✅ SendGrid email sent to {user.email}! Status: {response.status_code}")
                print(f"📧 Reset link: {reset_link}")
                
            except Exception as e:
                print(f"❌ Failed to send email to {user.email}: {e}")
                # Still return success to user, but log the error
                pass
            
            return Response({
                "message": "Password reset link has been sent to your email."
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            print(f"Password reset requested for non-existent email: {email}")
            return Response({
                "error": "No account found with this email address."
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Confirm password reset with JWT token
    """
    print(f"=== PASSWORD RESET CONFIRM ===")
    print(f"Request data: {request.data}")
    
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            print(f"UID received: {uid}")
            print(f"Token received: {token}")
            
            # Decode UID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id, is_active=True)
            
            print(f"User found: {user.username} (ID: {user.id})")
            
            # Verify JWT token
            try:
                # Decode the token to verify it's valid
                decoded_token = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=["HS256"]
                )
                
                print(f"Decoded token: {decoded_token}")
                
                # Check if the token belongs to this user
                if decoded_token.get('user_id') == user.id:
                    # Set new password
                    user.set_password(new_password)
                    user.save()
                    
                    print("Password reset successful!")
                    
                    return Response({
                        "message": "Password has been reset successfully. You can now login with your new password."
                    }, status=status.HTTP_200_OK)
                else:
                    print(f"Token user_id {decoded_token.get('user_id')} doesn't match user ID {user.id}")
                    return Response({
                        "error": "Invalid reset token."
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except jwt.ExpiredSignatureError:
                print("JWT token expired")
                return Response({
                    "error": "Reset token has expired. Please request a new reset link."
                }, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError as e:
                print(f"JWT token invalid: {e}")
                return Response({
                    "error": "Invalid reset token."
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (CustomUser.DoesNotExist, TypeError, ValueError, OverflowError) as e:
            print(f"Error finding user: {e}")
            return Response({
                "error": "Invalid reset link."
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        print(f"Serializer errors: {serializer.errors}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for authenticated users
    Expects: {"old_password": "current_password", "new_password": "new_password"}
    """
    user = request.user
    
    if not user.check_password(request.data.get('old_password')):
        return Response({
            "error": "Current password is incorrect."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    new_password = request.data.get('new_password')
    if not new_password:
        return Response({
            "error": "New password is required."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 6:
        return Response({
            "error": "New password must be at least 6 characters long."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        "message": "Password changed successfully."
    }, status=status.HTTP_200_OK)
    