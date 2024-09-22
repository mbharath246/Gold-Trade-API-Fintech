from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import CustomUser
from users.serializers import CustomUserSerializer, PasswordResetSerializer
from authtoken.views import get_token_user_data



class UsersListView(APIView):
    queryset = CustomUser.objects
    serializer_class = CustomUserSerializer
    data = {}

    def get(self, request):
        """
        API view for retrieving a list of all users.

        This endpoint allows users with proper authentication and permissions to retrieve a list of all users.
        The API response includes the success status, a message, the list of users, and the HTTP status code.

        **Request**:
        - GET /users/v1/list/

        **Responses**:
        - 200 OK: 
        - Description: The list of users was retrieved successfully.
        - Response Body:
            - success: bool, indicates if the retrieval was successful
            - message: str, confirmation message
            - data: list, a list of user details
            - status_code: int, HTTP status code (200)
        - 401 Unauthorized:
        - Description: The request was unauthorized due to invalid or expired token or insufficient permissions.
        - Response Body:
            - success: bool, indicates if the retrieval failed
            - message: str, error message
            - data: None
            - status_code: int, HTTP status code (401)            
        - 204 No Content:
        - Description: No users were found.
        - Response Body:
            - success: bool, indicates that no users were found
            - message: str, confirmation message
            - data: None
            - status_code: int, HTTP status code (204)
        """

        user_id, email, username = get_token_user_data(request)
        if not user_id or not email or not username:
            self.data['success'] = False
            self.data['message'] = "token is invalid or expired"
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_401_UNAUTHORIZED
            return Response(data=self.data, status=status.HTTP_401_UNAUTHORIZED)     
               
        user = self.queryset.get(id=user_id)

        if not user.is_superuser:
            self.data['success'] = False
            self.data['message'] = "insufficient permissions to access user details"
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_401_UNAUTHORIZED
            return Response(data=self.data, status=status.HTTP_401_UNAUTHORIZED) 
          
        instance = self.queryset.all()
        if not instance:
            self.data['success'] = False
            self.data['message'] = "user's Doesn't Exists"
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_204_NO_CONTENT
            return Response(data=self.data, status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.serializer_class(instance, many=True)
        self.data['success'] = True
        self.data['message'] = "list of all user's data"
        self.data['count'] = f'{len(serializer.data)} users present'
        self.data['data'] = serializer.data
        self.data['status_code'] = status.HTTP_200_OK
        return Response(data=self.data, status=status.HTTP_200_OK)


class CreateUser(APIView):
    queryset = CustomUser.objects
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    data = {}

    @swagger_auto_schema(
        operation_summary="Create a new user",
        request_body=CustomUserSerializer,
    )
    def post(self, request):
        """
        API view for creating a new user.

        This endpoint allows users to create a new user by providing user details in the request body.
        The data is validated and saved to the database if valid. The API response includes the success status,
        a message, the created user data, and the HTTP status code.

        **Request**:
        - POST /users/v1/create/
        
        **Request Body**:
        - application/json
        - Content-Type: application/json
        - Required fields :
        - `name`: str, required, name of the user
        - `email`: str, required, unique email address of the user
        - `password`: str, required, password for the user
        - `dob`: str, required, date of birth for the user

        **Responses**:
        - 201 Created: 
        - Description: The user was created successfully.
        - Response Body:
            - success: bool, indicates if the creation was successful
            - message: str, confirmation message
            - data: object, the created user details
            - status_code: int, HTTP status code (201)
        - 400 Bad Request:
        - Description: The request data was invalid or incomplete.
        - Response Body:
            - success: bool, indicates if the creation failed
            - message: str, error message
            - data: object, error details
            - status_code: int, HTTP status code (400)
        """
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.data['success'] = True
            self.data['message'] = "user has been created Successfully"
            self.data['data'] = serializer.data
            self.data['status_code'] = status.HTTP_201_CREATED

            return Response(data=self.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserDetailView(APIView):
    queryset = CustomUser.objects
    serializer_class = CustomUserSerializer
    data = {}

    def get(self, request):
        """
        API view for retrieving details of a user.

        This endpoint allows authenticated users to retrieve their own user details. It uses the token
        from the request to verify the user's identity and fetch their details. The API response includes
        the success status, a message, the user details, and the HTTP status code.

        **Request**:
        - GET /users/v1/details/

        **Responses**:
        - 200 OK:
            - Description: The user details were retrieved successfully.
            - Response Body:
                - success: bool, indicates if the retrieval was successful
                - message: str, confirmation message
                - data: object, the user details
                - status_code: int, HTTP status code (200)
        - 401 Unauthorized:
            - Description: The token is invalid or expired.
            - Response Body:
                - success: bool, indicates if the retrieval failed
                - message: str, error message
                - data: None
                - status_code: int, HTTP status code (401)
        - 404 Not Found:
            - Description: The user does not exist.
            - Response Body:
                - success: bool, indicates that the user was not found
                - message: str, confirmation message
                - data: None
                - status_code: int, HTTP status code (404)
        """
        user_id, email, username = get_token_user_data(request)
        if not user_id or not email or not username:
            self.data['success'] = False
            self.data['message'] = "token is invalid or expired"
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_401_UNAUTHORIZED
            return Response(data=self.data, status=status.HTTP_401_UNAUTHORIZED)   
                 
        instance = self.queryset.filter(id=user_id, email=email).first()
        if not instance:
            self.data['success'] = False
            self.data['message'] = "user doesn't exists."
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_404_NOT_FOUND
            return Response(data=self.data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(instance)

        self.data['success'] = True
        self.data['message'] = "user details."
        self.data['data'] = serializer.data
        self.data['status_code'] = status.HTTP_200_OK

        return Response(data=self.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=serializer_class,
        operation_summary="update user details"
    )
    def put(self, request):
        """
        API view for updating user details.

        This endpoint allows authenticated users to update their own details by providing the updated
        information in the request body. The data is validated and updated if valid. The API response includes
        the success status, a message, the updated user details, and the HTTP status code.

        **Request**:
        - PUT /users/v1/details/

        **Request Body**:
        - application/json
        - Content-Type: application/json
        - Required fields:
            - `name`: str, required, name of the user
            - `email`: str, optional, new email address for the user
            - `password`: str, optional, new password for the user
            - `username`: str, optional, new username for the user
            - `dob`: str, required, date of birth for the user

        **Responses**:
        - 200 OK:
            - Description: The user details were updated successfully.
            - Response Body:
                - success: bool, indicates if the update was successful
                - message: str, confirmation message
                - data: object, the updated user details
                - status_code: int, HTTP status code (200)
        - 401 Unauthorized:
            - Description: The token is invalid or expired.
            - Response Body:
                - success: bool, indicates if the update failed
                - message: str, error message
                - data: None
                - status_code: int, HTTP status code (401)
        - 404 Not Found:
            - Description: The user does not exist.
            - Response Body:
                - success: bool, indicates that the user was not found
                - message: str, confirmation message
                - data: None
                - status_code: int, HTTP status code (404)
        - 400 Bad Request:
            - Description: The request data was invalid or incomplete.
            - Response Body:
                - success: bool, indicates if the update failed
                - message: str, error message
                - data: object, error details
                - status_code: int, HTTP status code (400)
        """
        user_id, email, username = get_token_user_data(request)
        if not user_id or not email or not username:
            self.data['success'] = False
            self.data['message'] = "token is invalid or expired"
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_401_UNAUTHORIZED
            return Response(data=self.data, status=status.HTTP_401_UNAUTHORIZED)   
                 
        instance = self.queryset.filter(id=user_id, email=email).first()
        if not instance:
            self.data['success'] = False
            self.data['message'] = "user doesn't exists."
            self.data['data'] = None
            self.data['status_code'] = status.HTTP_404_NOT_FOUND
            return Response(data=self.data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            self.data['success'] = True
            self.data['message'] = "user details has been updated successfully"
            self.data['data'] = serializer.data
            self.data['status_code'] = status.HTTP_200_OK
            return Response(data=self.data, status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetView(APIView):
    queryset = CustomUser.objects
    serializer_class = PasswordResetSerializer
    data = {}
    

    @swagger_auto_schema(
        request_body=serializer_class,
        operation_summary="forget user password"
    )
    def put(self, request):
        """
        API view for updating a user's password.

        This endpoint allows users to update their password by providing the new password in the request body.
        The data is validated and updated if valid. The API response includes the success status,
        a message, the updated user data, and the HTTP status code.

        **Request**:
        - PUT /users/v1/reset/

        **Request Body**:
        - application/json
        - Content-Type: application/json
        - Required fields :
            - `email`: str, required.
            - `password`: str, required, the new password for the user.
            - `confirm_password`: str, required, to check new password for the user.

        **Responses**:
        - 200 OK: 
            - Description: The password was updated successfully.
            - Response Body:
                - success: bool, indicates if the update was successful
                - message: str, confirmation message
                - data: object, the updated user details
                - status_code: int, HTTP status code (200)
        - 400 Bad Request:
            - Description: The request data was invalid or incomplete.
            - Response Body:
                - success: bool, indicates if the update failed
                - message: str, error message
                - data: object, error details
                - status_code: int, HTTP status code (400)
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            self.data['success'] = True
            self.data['message'] = "user password has been updated successfully"
            self.data['data'] = serializer.data
            self.data['status_code'] = status.HTTP_200_OK
            return Response(data=self.data, status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)