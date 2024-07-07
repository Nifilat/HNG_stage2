from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from django.contrib.auth import authenticate

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
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
        }, status=status.HTTP_400_BAD_REQUEST)

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

# class OrganisationListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         organisations = request.user.organisations.all()
#         return Response({
#             "status": "success",
#             "message": "Organisations retrieved",
#             "data": OrganisationSerializer(organisations, many=True).data
#         }, status=status.HTTP_200_OK)

# class OrganisationDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, orgId):
#         organisation = Organisation.objects.filter(orgId=orgId, users=request.user).first()
#         if organisation:
#             return Response({
#                 "status": "success",
#                 "message": "Organisation record retrieved",
#                 "data": OrganisationSerializer(organisation).data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             "status": "Bad request",
#             "message": "Organisation not found"
#         }, status=status.HTTP_404_NOT_FOUND)

# class CreateOrganisationView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = OrganisationSerializer(data=request.data)
#         if serializer.is_valid():
#             organisation = serializer.save()
#             organisation.users.add(request.user)
#             return Response({
#                 "status": "success",
#                 "message": "Organisation created successfully",
#                 "data": OrganisationSerializer(organisation).data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "status": "Bad request",
#             "message": "Client error",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class AddUserToOrganisationView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, orgId):
#         userId = request.data.get('userId')
#         organisation = Organisation.objects.filter(orgId=orgId, users=request.user).first()
#         if organisation:
#             user = User.objects.filter(userId=userId).first()
#             if user:
#                 organisation.users.add(user)
#                 return Response({
#                     "status": "success",
#                     "message": "User added to organisation successfully"
#                 }, status=status.HTTP_200_OK)
#         return Response({
#             "status": "Bad request",
#             "message": "Organisation or User not found"
#         }, status=status.HTTP_404_NOT_FOUND)

class OrganisationViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the organisations the current user is part of
        return self.request.user.organisations.all()

    def perform_create(self, serializer):
        organisation = serializer.save()
        organisation.users.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_user(self, request, orgId):
        userId = request.data.get('userId')
        organisation = self.get_object()
        
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
            "message": "User or organisation not found"
        }, status=status.HTTP_404_NOT_FOUND)

