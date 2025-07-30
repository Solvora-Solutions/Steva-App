from django.contrib import admin
from django import forms
from .models import Parent
from Users.models import User
from Student.models import Student

class UserInlineForm(forms.ModelForm):
    """Form for inline user details in Parent admin."""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

class UserInline(admin.StackedInline):
    model = User
    form = UserInlineForm
    can_delete = False
    verbose_name_plural = 'User Details'
    fk_name = 'parent_profile'  # Link to Parent via OneToOne

class StudentInline(admin.TabularInline):
    model = Student.parents.through
    extra = 1

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_first_name', 'user_last_name', 'phone_number', 'linked_students')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
    list_filter = ('created_at',)
    inlines = [StudentInline]
    
    def user_email(self, obj):
        return obj.user.email
    
    def user_first_name(self, obj):
        return obj.user.first_name
    
    def user_last_name(self, obj):
        return obj.user.last_name
    
    def linked_students(self, obj):
        return ", ".join([f"{s.first_name} {s.last_name}" for s in obj.students.all()])
