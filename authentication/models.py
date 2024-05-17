from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, Permission, PermissionsMixin
from django.db import models    
class CustomUserManger (BaseUserManager):
    def create_user(self, username, email, password, phone_number, is_organization, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, is_organization=is_organization, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self,username,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        print("extra kwargs",extra_fields)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must have is_staff=True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have a superuser=True')
        
        user = self.model(
            username=username,
            email = email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    phone_number = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profile_image', blank=True, null=True)
    is_organization = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(Group,
                                    verbose_name='groups',
                                    blank=True,
                                    related_name='group_related_user',
                                    related_query_name='group_user')
    
    user_permissions = models.ManyToManyField(Permission,verbose_name=  'user permissions', blank=True, help_text="Specific permissions for the user", related_name='permission_user', related_query_name='permission_related_user') 
    
    is_organization = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManger()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','password']
    
    def save(self, *args, **kwargs):
        if self.is_organization:
            self.is_staff = True
            
        super().save(*args, **kwargs)
        

    def __str__(self) -> str:
        return self.username
    