from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListView, OrganisationDetailView, CreateOrganisationView, AddUserToOrganisationView

urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('api/users/<uuid:id>', UserDetailView.as_view()),
    path('api/organisations', OrganisationListView.as_view()),
    path('api/organisations/<uuid:orgId>', OrganisationDetailView.as_view()),
    path('api/organisations/create', CreateOrganisationView.as_view()),
    path('api/organisations/<uuid:orgId>/users', AddUserToOrganisationView.as_view()),
]
