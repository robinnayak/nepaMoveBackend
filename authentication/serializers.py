from  rest_framework import serializers
from .models  import CustomUser,Organization,Driver
from django.contrib.auth.hashers import check_password

class CustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)    
    class Meta:
        model = CustomUser
        fields = ['id','username','password','password2','email','phone_number','is_organization','is_driver']   
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
    def validate(self, data):
        
        if 'phone_number' in data:
            if len(data['phone_number']) != 10:
                raise serializers.ValidationError("Phone number must be 10 digits")
        if 'username' in data:
            if CustomUser.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError("Username already exists")  

        password = data.get('password')
        password2 = data.get('password2')
        
        if password != password2:
            raise serializers.ValidationError("Passwords must match") 
        print("valiodated data: ",data)
        return data
    
    def create(self, validated_data):
        print("create valiodated data: ",validated_data)
        
        validated_data.pop('password2') 
        user = CustomUser.objects.create_user(**validated_data)  
        return user
    
    def to_representation(self, instance):
        print("instance data: ",instance)
        
        request = self.context.get('request')   
        method  = request.method if request else None
        if method == 'GET':
            self.fields.pop('password2',None) 
        
        return super().to_representation(instance)         
    


class CustomUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        # if 'username' in data:
        #     if not CustomUser.objects.filter(username=data['username']).exists():
        #         raise serializers.ValidationError("User not found")
            
        # if 'password' in data:
        #     if len(data['password']) < 8:
        #         raise serializers.ValidationError("Password must be atleast 8 characters")
            
        if 'password' in data and 'username' in data:
            user = CustomUser.objects.get(username=data['username'])
            if not user:
                raise serializers.ValidationError("User not found") 
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Invalid password")
        return data 
    
class OrganizationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Organization
        fields = '__all__'   
    
    def update(self, instance, validated_data):
        # check_driver = self.context.get('check_driver')
        # driver_license = self.context.get('driver_license')
        # print("check_driver: ",check_driver)
        # print("validated data: ",validated_data)
        # print("instance data: ",instance.user.email)
        phone_number = self.context.get('phone_number')
        if phone_number:
            user_serializer = CustomUserSerializer(instance.user)
            # print("user_serializer data: ",user_serializer.data)
            if user_serializer.data['phone_number'] != phone_number:
                user = instance.user
                user.phone_number = phone_number
                user.save()
        
        # if check_driver:
        #     driver = Driver.objects.get(license_number=driver_license)
        #     instance.driver = driver
        #     print("instance driver: ",instance.driver)
        #     instance.save()
            
        # print("instance driver outside: ",instance.driver)
            
            
            
        
        # if phone_number:
        #     user = instance.user
        #     user.username = user.username
        #     user.email = user.email
        #     user.phone_number = phone_number
        #     # user.is_organization = user_data.get('is_organization',user.is_organization)
        #     user.is_organization = user.is_organization
        #     user.is_driver = user.is_driver
        #     user.save()
        
        return super().update(instance, validated_data)   
  
class DriverSerializer(serializers.ModelSerializer):

    
    
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Driver
        fields = '__all__'
    def update(self, instance, validated_data):
        # print("validated data: ",validated_data)
        check_organization = self.context.get('check_organization')
        org_email = self.context.get('org_email')
        phone_number = self.context.get('phone_number')
        
        if check_organization:
            organization = Organization.objects.get(user__email=org_email)
            instance.organization = organization
            print("instance driver: ",instance.organization)
            instance.save()
        if phone_number:
            user_serializer = CustomUserSerializer(instance.user)
            # print("user_serializer data: ",user_serializer.data)
            if user_serializer.data['phone_number'] != phone_number:
                user = instance.user
                user.phone_number = phone_number
                user.save()
            
        return super().update(instance, validated_data)
    
        

