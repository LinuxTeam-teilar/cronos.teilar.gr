from cronos.accounts.models import UserProfile
from django.conf.urls.defaults import url
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource

class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'profile'
        excludes = ['dionysos_password', 'eclass_password', 'webmail_password']
        include_resource_uri = False
        include_absolute_uri = False

class UserResource(ModelResource):
    profile = fields.ForeignKey(UserProfileResource, 'userprofile', full=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['date_joined', 'id', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password']
        allowed_methods = ['get', 'post']
        include_resource_uri = False
        include_absolute_uri = False
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(username=request.user.username)

    def override_urls(self):
        return [url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),]
