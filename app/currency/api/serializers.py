from rest_framework import serializers

from app.currency.models import UserCurrency, Currency


class UserCurrencySerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления пользователем отслеживаемой валюты."""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
    )
    threshold = serializers.DecimalField(
        decimal_places=4,
        max_digits=10,
    )

    class Meta:
        model = UserCurrency
        fields = ('user', 'currency', 'threshold')


class DailyPricesSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения последних загруженных котировок."""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    id = serializers.IntegerField(source='currency_id')
    date = serializers.DateField()
    charcode = serializers.CharField(source='currency.char_code')
    value = serializers.DecimalField(
        decimal_places=4,
        max_digits=10,
    )

    class Meta:
        model = UserCurrency
        fields = ('user', 'id', 'date', 'charcode', 'value')
