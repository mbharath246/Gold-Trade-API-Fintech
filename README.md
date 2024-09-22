# Gold Trading API.

## Overview
This project provides a set of APIs for managing users' gold trading activities, including buying, selling gold, checking gold prices, managing user balance, and fetching transaction history. The APIs use Django, Django REST Framework, and are secured with JWT authentication.

## Features

- **Buy Gold**: Allows users to purchase gold.
- **Sell Gold**:  Allows users to sell gold.
- **Check Gold Price**: Retrieve the current gold price.
- **Deposit Money**: Users can deposit money into their accounts.
- **Transaction History**: Fetch paginated transaction history.
- **User Details**: Fetch the current user’s gold and balance details.
- **Swagger Documentation**: API documentation available via Swagger.

## Prerequisites

- Python 3.8+
- Django 5.0.7+
- Django-Rest_framework 3.15.2
- Redis (for caching)
- Docker (Optional)
- Git

### Setting Up Locally Backend

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mbharath246/Gold-Trade-API-Fintech.git
   cd Gold-Trade-API-Fintech
   ```
2. **Create and activate a virtual environment:**
    ```bash
    python -m venv env # On Windows `env\Scripts\activate`
    virtualenv env  # On Linux use `source env/bin/activate`
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    Optional: ( install docker : https://docs.docker.com/engine/install/ubuntu/)
    ```
4. **Set up for the project:**
    ```bash
    Windows: python manage.py runserver
    
    Docker : docker compose up
    ```
5. **Run the development server:** <br>
    **Note 1**: Before starting the server if you are running on windows make sure to run redis server locally,
              You can start the Redis server using the following command  `redis-server` <br>
   **Note 2**: If you are running in Docker no need to start the redis just start `docker compose up`
    
    ```bash
    http://127.0.0.1:8000/swagger
    ```
7. **Additional Steps**
    - Create User
    - User Login to get Token
    - Authorize Token
    - Now you can use all apis.
8. **Super User Credentials**
   - Username: `bharath@gmail.com`
   - password: `12345`


## Images

## Swagger ui for all apis

 ![image](https://github.com/user-attachments/assets/ebd55e2f-53d2-47c3-b08d-fac08514750e)

## Login API

 ![image](https://github.com/user-attachments/assets/ba293482-b60c-451b-b457-bce5120d09d1)

## Jwt Authentication

 ![image](https://github.com/user-attachments/assets/ceb95a1c-ef49-4500-a068-388939eec103)

## Redis Server
**if you are getting this run redis server see next image**
 ![image](https://github.com/user-attachments/assets/0df83d8b-212c-4f03-a117-a3d1bdfbdf9e)

## Redis Server Start

 ![image](https://github.com/user-attachments/assets/59729550-0b96-45ca-accb-9a6e31b24e75)

## Check Gold Price

 ![image](https://github.com/user-attachments/assets/02f8dd24-8f03-4328-a114-031407180ff7)

## Get the all details of a gold

 ![image](https://github.com/user-attachments/assets/675c9c27-142b-4d3d-bd07-98d767e4d9b7)

## Purchase a gold

 ![image](https://github.com/user-attachments/assets/6b9c19fd-b70e-46b7-84c4-426fbba0535d)

## Sell a Gold

 ![image](https://github.com/user-attachments/assets/bea2a169-3dae-42dc-b5ae-4ce5db58b50c)

## Transactions

![image](https://github.com/user-attachments/assets/1cc0f207-cba4-4e73-a5e7-9fa4afb64ff3)
