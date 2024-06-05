import datetime
from datetime import timedelta

from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.email import TemplateEmail

from .models import PasswordResetToken, Plan, User
from .serializers import PlanSerializer, UserRegisterSerializer, UserSerializer
from .utils import get_tokens_for_user


class UserRegisterApi(APIView):
    """
    View to register new customers
    * Requires no authentication.
    * Non logged in users are able to access this view.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        registered_user = serializer.save()

        PasswordResetToken.objects.filter(user=registered_user).delete()
        code = PasswordResetToken.objects.create(user=registered_user)
        template = TemplateEmail(
            to=[registered_user.email],
            subject="Confirm Your Email",
            template="activate",
            context={"code": code, "user": registered_user},
        )
        template.send()
        return Response(
            UserSerializer(registered_user).data, status=status.HTTP_201_CREATED
        )


class UserLoginApi(APIView):
    """
    View to log in customers
    * Requires no authentication.
    * Non logged in users are able to access this view.
    """

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        response = Response()
        if (email is None) or (password is None):
            raise exceptions.AuthenticationFailed(
                "You must enter an email and password."
            )
        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed(
                "We couldn't find an account for this email. Try again."
            )
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(
                "You entered an invalid password. Try again."
            )

        token = get_tokens_for_user(user)
        response.data = token
        return response


class UserMeApi(APIView):
    """
    View to current logged in user
    * Requires authentication.
    * Non logged in users are unable to access this view.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        plan, created = Plan.objects.get_or_create(user=request.user)
        if created:
            today = datetime.date.today()
            plan.expiry_date = today + timedelta(days=7)
            plan.save()
        if plan.remaining_days == 0 and plan.plan != "Free":
            today = datetime.date.today()
            plan.plan = "Free"
            plan.expiry_date = today + timedelta(days=365)
            plan.save()
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "plan": PlanSerializer(plan).data,
            },
            status=status.HTTP_200_OK,
        )


class UserDetailView(APIView):
    def patch(self, request, uuid, format=None):
        user = User.objects.get(id=uuid)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, format=None):
        user = User.objects.get(id=uuid)
        user.is_active = False
        user.save()
        # user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPasswordResetApi(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data["email"]
        action = request.data["action"]

        if not User.objects.filter(email=email).exists():
            return Response(
                {
                    "success": False,
                    "message": "We couldn't find a user with that email.",
                },
                status=status.HTTP_200_OK,
            )

        user = User.objects.get(email=email)
        PasswordResetToken.objects.filter(user=user).delete()
        code = PasswordResetToken.objects.create(user=user)
        if action == "reset":
            template = TemplateEmail(
                to=[email],
                subject="Reset Your Password",
                template="reset",
                context={"code": code, "user": user},
            )
            template.send()

        if action == "resend":
            if not user.email_confirmed:
                template = TemplateEmail(
                    to=[email],
                    subject="Confirm Your Email",
                    template="activate",
                    context={"code": code, "user": user},
                )
                template.send()
            else:
                return Response(
                    {
                        "success": False,
                        "message": "This email has already been confirmed.",
                    }
                )

        return Response(
            {"success": True, "message": "Check your inbox for instructions."},
            status=status.HTTP_200_OK,
        )


class TokenVerifyApi(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data["code"]
        email = request.data["email"]
        user = User.objects.get(email=email)

        token_object = PasswordResetToken.objects.filter(code=code, user=user)

        if token_object.exists():
            return Response(
                {"success": True, "message": "Token is valid"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Token doesn't exist or invalid"},
            status=status.HTTP_200_OK,
        )


class ActivateAccountApi(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data["code"]
        email = request.data["email"]
        user = User.objects.get(email=email)

        token_object = PasswordResetToken.objects.filter(code=code, user=user)

        if token_object.exists():
            user.email_confirmed = True
            user.save()
            return Response(
                {"success": True, "message": "Token is valid"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Token doesn't exist or invalid"},
            status=status.HTTP_200_OK,
        )


class UserSetNewPasswordApi(APIView):
    def post(self, request, *args, **kwargs):
        password = request.data.get("password")
        email = request.data.get("email")

        user = User.objects.get(email=email)

        user.set_password(password)
        user.save()

        return Response(
            {"success": True, "message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )
