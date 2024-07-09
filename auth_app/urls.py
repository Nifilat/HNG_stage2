from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, UserDetailView, OrganisationViewSet, AddUserToOrganisationView, OrganisationDetailView

class OptionalSlashRouter(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        optional_slash_urls = []
        for url in urls:
            optional_slash_urls.append(re_path(f'^{url.pattern}/?$', url.callback, name=url.name))
        return optional_slash_urls

router = OptionalSlashRouter()
router.register(r'organisations', OrganisationViewSet, basename='organisation')

urlpatterns = [
    re_path(r'^auth/register/?$', RegisterView.as_view()),
    re_path(r'^auth/login/?$', LoginView.as_view()),
    re_path(r'^api/users/(?P<id>[0-9a-f-]+)/?$', UserDetailView.as_view()),
    re_path(r'^api/organisations/?$', OrganisationViewSet.as_view({'get': 'list', 'post': 'create'})),  # Add this line
    path('api/', include(router.urls)),
    re_path(r'^api/organisations/(?P<orgId>[0-9a-f-]+)/?$', OrganisationDetailView.as_view()),
    re_path(r'^api/organisations/(?P<orgId>[0-9a-f-]+)/users/?$', AddUserToOrganisationView.as_view()),
]