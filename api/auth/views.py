from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.auth.forms import Register, Login
from api.auth.serializers import LogOutSerializer, LoginSerializer, SignUpSerializer, UserLoginSerializer, \
    VerifyCodeSerializer, \
    ReSendCodeSerializer
from api.tasks import send_sms
from common.users.models import Code

User = get_user_model()


class LoginAPIView(CreateAPIView):
    serializer_class = UserLoginSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_sms.apply_async([serializer.data.get("id"), serializer.data.get("phone")])
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyCodeAPIview(CreateAPIView):
    queryset = Code.objects.all()
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignInAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_sms.apply_async([serializer.validated_data.get('id'), serializer.validated_data.get('phone')])
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReSendCodeAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ReSendCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(phone=serializer.data.get('phone', None)).first()
        if user:
            code, created = Code.objects.get_or_create(user=user)
            return Response({"code": code.generate_code(), "guid": user.guid}, status=status.HTTP_200_OK)
        return Response({"code": None}, status=status.HTTP_200_OK)


class LogoutView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.data['refresh'])
        except:
            return Response({'message': "Token is blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
        token.blacklist()
        return Response(status=status.HTTP_200_OK)


def log_in(request):
    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            user = authenticate(request=request, phone=phone, password=password)
            if user:
                login(request, user)
                return render(request, 'login/enter_code.html', {"phone": phone})
    return render(request, 'login/login.html', {})


def log_out(request):
    logout(request)
    return redirect(log_in)


def register(request):
    if request.method == "POST":
        form = Register(request.POST)
        if form.is_valid():
            phone = request.POST.get('phone')
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                return redirect('register')
            form.save()
            try:
                user = authenticate(request=request, phone=phone, username=username, password=password1)
            except:
                return redirect('register')
            return render(request, 'login/enter_code.html', {"phone": phone})
    return render(request, 'login/register.html', {})


def user_detail(request):
    return render(request, 'login/user_detail.html', {})


def enter_code(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        verify_code = Code.objects.filter(user__phone=phone, number=code).first()
        if verify_code:
            return redirect('user_detail')
    return render(request, 'login/enter_code.html', {})


def index(request):
    return render(request, 'login/index.html', {})
