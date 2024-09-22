from django.urls import path
from apis import views


urlpatterns = [
    path('gold/price/',views.GoldPriceView.as_view(), name='gold-price'),
    path('user/gold-details/', views.UserGoldDetailsView.as_view(), name='user-gold-details'),
    path('gold/deposit/',views.DepositMoneyView.as_view(), name='money-deposit'),
    path('gold/buy/',views.BuyGoldView.as_view(), name='gold-buy'),
    path('gold/sell/',views.SellGoldView.as_view(), name='gold-sell'),
    path('gold/transaction-history/', views.GoldTransactionHistoryView.as_view(), name='transaction-history'),
]
