from rest_framework import serializers


class OrderItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True)
