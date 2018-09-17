from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import MyUser, MyUserManager, Profile, Post, UserAction, Notification

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('email','firstName', 'lastName', 'gender', 'age',)

    password1 = forms.CharField(label = 'Password', max_length = 100, widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirm Password', max_length = 100, widget = forms.PasswordInput)

    def clean_password2(self):
        # Check confirmation password
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password doesn't match.")
        return password2

    def save(self, commit = True):
        user = super().save(commit = False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'is_active', 'is_admin', 'firstName', 'lastName', 'gender', 'age')

    def clean_password(self):
        return self.initial['password']

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'is_admin',)
    list_filter = ('email', 'is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields' : ('firstName', 'lastName', 'gender', 'age', 'slug', 'following', 'block', 'blockNoti', 'newNotificationsNumber')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    readonly_fields = ('following', 'block', 'blockNoti')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstName', 'lastName', 'gender', 'age', 'password1', 'password2')}
        ),
    )

    search_field = ('email', 'firstName', 'lastName')
    ordering = ('email', 'firstName')
    filter_horizontal = ()


admin.site.register(MyUser, UserAdmin)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(UserAction)
admin.site.register(Notification)

admin.site.unregister(Group)