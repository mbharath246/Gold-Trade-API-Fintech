from rest_framework import serializers
from apis.models import GoldTransaction, Gold


class GoldSerializer(serializers.Serializer):
    grams = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_grams(self, value):
        if value <= 0:
            raise serializers.ValidationError("Grams to sell must be a positive number.")
        return value
    

class ListGoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gold
        fields = ['available_gold', 'available_balance', 'last_gold_sell', 'total_gold_sell', 'transaction_date']
    


class DepositMoneySerializer(serializers.Serializer):
    amount = serializers.FloatField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The deposit amount must be greater than zero.")
        if value >= 1000000:
            raise serializers.ValidationError("The deposit amount must be less than 1000000.")
        return value
    

class GoldTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransaction
        fields = [
            'transaction_type',
            'grams',
            'amount_in_currency',
            'transaction_date',
            'commission_rate'
        ]