from rest_framework import status, viewsets, mixins
from rest_framework.viewsets import ViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import RegisterSerializer, UserSerializer, OrganisationSerializer
from django.contrib.auth import authenticate

class RegisterView(APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            org = Organisation.objects.create(
                name=f"{user.firstName}'s Organisation"
            )
            org.users.add(user)
            token = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(token.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "errors": serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            token = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(token.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Authentication failed"
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = User.objects.filter(userId=id, organisations__in=request.user.organisations.all()).first()
        if user:
            return Response({
                "status": "success",
                "message": "User record retrieved",
                "data": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)



class OrganisationViewSet(ViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        user = self.request.user
        
        return Organisation.objects.filter(users=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {
            'status': 'success',
            'message': 'Fetched all organisations successfully',
            'data': {
                'organisations': serializer.data
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        organisation = Organisation.objects.filter(orgId=pk, users=request.user).first()
        if organisation:
            return Response({
                "status": "success",
                "message": "Organisation record retrieved",
                "data": self.serializer_class(organisation).data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Organisation not found"
        }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": self.serializer_class(organisation).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Client error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(APIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    

    def get(self, request, *args, **kwargs):
        org = self.get_object()
        if request.user in org.users.all():
            data = {
                'status': 'success',
                'message': 'Organisation details retrieved successfully',
                'data': OrganisationSerializer(org).data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Forbidden', 'message': 'You do not have access to this organisation'}, status=status.HTTP_403_FORBIDDEN)


class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        userId = request.data.get('userId')
        organisation = Organisation.objects.filter(orgId=orgId, users=request.user).first()
        if organisation:
            user = User.objects.filter(userId=userId).first()
            if user:
                organisation.users.add(user)
                return Response({
                    "status": "success",
                    "message": "User added to organisation successfully"
                }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Organisation or User not found"
        }, status=status.HTTP_404_NOT_FOUND)

