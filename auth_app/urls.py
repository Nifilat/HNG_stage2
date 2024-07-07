from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, UserDetailView, OrganisationViewSet, AddUserToOrganisationView


router = DefaultRouter()
router.register(r'organisations', OrganisationViewSet, basename='organisation')
urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('api/users/<uuid:id>', UserDetailView.as_view()),
    path('api/', include(router.urls)),
    # path('api/organisations', OrganisationListView.as_view()),
    # path('api/organisations/<uuid:orgId>', OrganisationDetailView.as_view()),
    # path('api/organisations', CreateOrganisationView.as_view()),
    path('api/organisations/<uuid:orgId>/users', AddUserToOrganisationView.as_view()),
]
