from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not username:
            raise ValueError('User must have a username')
        user = self.model(email = self.normalize_email(email),
                     first_name = first_name,
                     last_name = last_name,
                     username = username
                     )
        user.set_password(password) #predefined method to encrypt password
        user.save(using = self.db)  #save in the database
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
                     email = self.normalize_email(email),
                     first_name = first_name,
                     last_name = last_name,
                     username = username,
                     password=password,

               )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self.db) 
        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2
    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer')
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique = True)
    email = models.EmailField(max_length=100, unique = True)
    phone_number = models.CharField(max_length = 12, blank= True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank = True, null =  True)

    #required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    #use email as login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = UserManager() #to tell this class which usermanager to use on it
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def get_role(self):
        user_role = 'Vendor' if self.role == 1 else 'Customer'
        return user_role
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank =True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    zip_code = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.user.email