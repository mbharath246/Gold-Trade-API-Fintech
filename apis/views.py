from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from drf_yasg.utils import swagger_auto_schema
import redis
from redis.exceptions import ConnectionError
import requests
import threading


from apis.models import Gold, GoldTransaction
from apis.serializers import GoldSerializer, DepositMoneySerializer, GoldTransactionSerializer, ListGoldSerializer


lock = threading.Lock()

def get_redis_client():
    try:
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
        print(redis_client.ping())
        return redis_client
    except ConnectionError as e:
        print(f"Redis connection error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



class GoldPriceView(APIView):
    """
    Fetches the current gold price from a public API (Metals-API).
    """
    @swagger_auto_schema(operation_summary="Check Gold Price")
    def get(self, request, format=None):

        redis_client = get_redis_client()

        if not redis_client:
            return Response({
                'message':'Redis Connection error please start the redis server.'
            })
        redis_key = "gold_price_usd"
        cache_ttl = 3600  # TTL of 60 minutes (3600 seconds)

        cached_price = redis_client.get(redis_key)
        if cached_price:
            cache_gold_price = cached_price.decode('utf-8') 
            data = {
                'success': True,
                'message': 'Gold price details fetched successfully',
                'data': {
                    'price_per_ounce_USD': round(float(cache_gold_price), 2),
                    'price_per_1gram_USD': round(float(cache_gold_price) / 28.34, 2),
                    'price_per_ounce_INR': round(float(cache_gold_price) * 83, 2),
                    'price_per_1gram_INR': round((float(cache_gold_price) * 83) / 28.34, 2),
                    'source': 'redis cache'
                },
                'status': status.HTTP_200_OK
            }

            return Response(data=data, status=status.HTTP_200_OK)
        

        api_url = "https://api.metalpriceapi.com/v1/latest"
        params = {
            'api_key':settings.METALS_API_KEY,
            'base':'XAU',
            'currencies':'USD,INR'
        }
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                gold_price = data.get('rates', {}).get('USD', None)
                if gold_price:
                    redis_client.setex(redis_key, cache_ttl, gold_price)
                    return Response({
                        'success': True,
                        'message': 'Gold price details fetched successfully',
                        'data': {
                            'price_per_ounce_usd': round(float(gold_price), 2),
                            'price_per_1gram_USD': round(float(gold_price) / 28.34, 2),
                            'price_per_ounce_INR': round(float(gold_price) * 83, 2),
                            'price_per_1gram_INR': round((float(gold_price) * 83) / 28.34, 2),
                        },
                        'status': status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({
                        'error': 'Could not retrieve gold price'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'error': 'Failed to connect to the gold price API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserGoldDetailsView(APIView):

    @swagger_auto_schema(operation_summary="Check Gold Details.")
    def get(self, request):
        """
        This Api is used to get the all the details of a Gold.
        """
        user = request.user
        try:
            gold_record = Gold.objects.get(user=user)
            serializer = ListGoldSerializer(gold_record)
            data = {
                'success': True,
                'message': 'Gold details fetched successfully',
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
            return Response(data=data, status=status.HTTP_200_OK)

        except Gold.DoesNotExist:
            return Response({'error': 'No gold details found for this user'}, status=status.HTTP_404_NOT_FOUND)
        

class DepositMoneyView(APIView):

    queryset = Gold.objects
    serializer_class = DepositMoneySerializer

    @swagger_auto_schema(
            request_body=serializer_class,
            operation_summary="Deposit money",
    )
    def post(self, request):
        """
        This Api is used to deposit the user money in form of INR.
        """
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if serializer.is_valid():
            deposit_amount = serializer.validated_data['amount']

            try:
                exists = self.queryset.filter(user=user).exists()
                if not exists:
                    instance = self.queryset.create(user=user)
                    instance.save()
                with lock:
                    with transaction.atomic():
                        gold_record = get_object_or_404(self.queryset.select_for_update(), user=request.user)

                        gold_record.available_balance += float(deposit_amount)
                        gold_record.save()

                        GoldTransaction.objects.create(
                            user=user,
                            transaction_type='deposit',
                            grams=0,
                            amount_in_currency=Decimal(deposit_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                            commission_rate=0
                        )

                return Response({
                    "sucess":True,
                    'message': 'Money deposited successfully',
                    "data":{'available_balance': gold_record.available_balance},
                    "status": status.HTTP_200_OK
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class BuyGoldView(APIView):
    queryset = Gold.objects
    serializer_class = GoldSerializer

    @swagger_auto_schema(
            request_body=serializer_class,
            operation_summary="Buy Gold",
    )
    def post(self, request):
        """
        This Api is used to purchase the gold.
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            grams_to_buy = serializer.validated_data['grams']
            commission_rate = Decimal('0.02')
        
            gold_object = GoldPriceView.get(self=self,request=request).data
            gold_price = gold_object.get('data', {}).get('price_per_1gram_INR', None)
            
            if not gold_price:
                return Response({'error': 'Could not retrieve gold price'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            gold_price = Decimal(gold_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            cost_inr = Decimal(grams_to_buy) * gold_price
            cost_inr = cost_inr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            total_cost_inr = cost_inr * (1 + commission_rate)
            total_cost_inr = total_cost_inr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            try:
                exists = self.queryset.filter(user=user).exists()
                print(exists, 'EXISTS')

                if not exists:
                    instance = self.queryset.create(user=user)
                    instance.save()

                with lock:
                    with transaction.atomic():
                        gold_record = get_object_or_404(self.queryset.select_for_update(), user=user)
                        print(gold_record.available_balance)
                        if gold_record.available_balance < total_cost_inr:
                            return Response({'error': 'insufficient balance, please deposit money to purchase gold.'}, status=status.HTTP_400_BAD_REQUEST)

                        gold_record.available_balance -= total_cost_inr.__float__()
                        gold_record.available_gold += float(grams_to_buy)
                        gold_record.save()

                        GoldTransaction.objects.create(
                            user=user,
                            transaction_type='buy',
                            grams=float(grams_to_buy),
                            amount_in_currency=total_cost_inr,
                            commission_rate=commission_rate
                        )

                return Response({
                    "success":True,
                    'message': 'Gold purchased successfully',
                    "data": {
                        'available_balance': gold_record.available_balance,
                        'available_gold': gold_record.available_gold
                    },
                    "status":status.HTTP_200_OK
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           


class SellGoldView(APIView):
    queryset = Gold.objects
    serializer_class = GoldSerializer


    @swagger_auto_schema(
            request_body=serializer_class,
            operation_summary="Sell Gold",
    )
    def post(self, request):
        """
        This Api is used to sell the Gold.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            grams_to_sell = serializer.validated_data['grams']
            commission_rate = Decimal(0.02)

            gold_object = GoldPriceView.get(self=self,request=request).data
            gold_price = gold_object.get('data',{}).get('price_per_1gram_INR', None)
            if not gold_price:
                return Response({'error': 'Could not retrieve gold price'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                with lock:
                    with transaction.atomic():
                        gold_record = get_object_or_404(Gold.objects.select_for_update(), user=request.user)
                        if gold_record.available_gold < float(grams_to_sell):
                            return Response({'error': 'Insufficient gold balance'}, status=status.HTTP_400_BAD_REQUEST)

                        sale_amount_inr = float(grams_to_sell) * float(gold_price)
                        total_sale_inr = sale_amount_inr * (1 - commission_rate).__float__()

                        gold_record.available_gold -= float(grams_to_sell)
                        gold_record.available_balance += total_sale_inr
                        gold_record.last_gold_sell = float(grams_to_sell)

                        gold_record.total_gold_sell += float(grams_to_sell)

                        gold_record.save()

                        GoldTransaction.objects.create(
                            user=request.user,
                            transaction_type='sell',
                            grams=float(grams_to_sell),
                            amount_in_currency=sale_amount_inr,
                            commission_rate=commission_rate
                        )

                return Response({
                    "success":True,
                    'message': 'Gold sold successfully',
                    "data": {
                        'available_balance': gold_record.available_balance,
                        'available_gold': gold_record.available_gold,
                        'total_selling_gold': gold_record.total_gold_sell
                    },
                    "status":status.HTTP_200_OK
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GoldTransactionPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100

class GoldTransactionHistoryView(generics.ListAPIView):
    serializer_class = GoldTransactionSerializer
    pagination_class = GoldTransactionPagination

    def get_queryset(self):
        """
        This Api is used to get the all the transactions of a user.
        """
        return GoldTransaction.objects.filter(user=self.request.user).order_by('-transaction_date')