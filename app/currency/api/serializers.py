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


class RatesSerializer(serializers.ModelSerializer):
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


class AnalyticsSerializer(serializers.ModelSerializer):
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
    threshold_match_type = serializers.CharField(default='no threshold')
    percentage_ratio = serializers.DecimalField(decimal_places=2, max_digits=10, default=None)
    is_max_value = serializers.BooleanField()
    is_min_value = serializers.BooleanField()

    class Meta:
        model = UserCurrency
        fields = (
            'user', 'id', 'date', 'charcode', 'value', 'is_max_value',
            'is_min_value', 'threshold_match_type', 'percentage_ratio',
        )
