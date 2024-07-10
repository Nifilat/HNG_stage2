from rest_framework import status, viewsets, mixins
from rest_framework.viewsets import ViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import get_object_or_404
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
            "message": "Invalid Credentials"
        }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = User.objects.filter(
            userId=id, organisations__in=request.user.organisations.all()).first()
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


class OrganisationViewSet(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return Organisation.objects.filter(users=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Fetched all organisations successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)

    # def retrieve(self, request, pk=None):
    #     organisation = Organisation.objects.filter(orgId=pk, users=request.user).first()
    #     if organisation:
    #         serializer = self.get_serializer(organisation)
    #         return Response({
    #             "status": "success",
    #             "message": "Organisation record retrieved",
    #             "data": serializer.data
    #         }, status=status.HTTP_200_OK)
    #     return Response({
    #         "status": "Bad request",
    #         "message": "Organisation not found"
    #     }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orgId):
        try:
            org = get_object_or_404(Organisation, orgId=orgId)
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Organisation not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user in org.users.all():
            data = {
                'status': 'success',
                'message': 'Organisation details retrieved successfully',
                'data': OrganisationSerializer(org).data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Forbidden',
                'message': 'You do not have access to this organisation'
            }, status=status.HTTP_403_FORBIDDEN)


class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        userId = request.data.get('userId')
        organisation = Organisation.objects.filter(
            orgId=orgId, users=request.user).first()
        try:
            if not organisation:
                raise Organisation.DoesNotExist

            user = User.objects.get(userId=userId)
            if not user:
                raise User.DoesNotExist

            organisation.users.add(user)
            return Response({
                "status": "success",
                "message": "User added to organisation successfully"
            }, status=status.HTTP_200_OK)

        except Organisation.DoesNotExist:
            return Response({
                "status": "Not Found",
                "message": "Organisation not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except User.DoesNotExist:
            return Response({
                "status": "Not Found",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "Error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
