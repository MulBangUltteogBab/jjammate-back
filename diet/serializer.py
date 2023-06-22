from rest_framework import serializers


class StackDietSerializer(serializers.Serializer):
    military_number = serializers.ListField(default=[
        "6335", "3389", "2171", "8623", "1691", "5322", "9030", "6282", "7369", 
        "5021", "8902", "3296", "6176", "7652", "1570", "7162", "1968", "3182", 
        "2291", "2621", "3007", "5397", "1862", "2136", "6685", "5861", "7296"
    ])


class GetDietSerializer(serializers.Serializer):
    military_number = serializers.IntegerField(default=6335)


class GetPXFoodSerializer(serializers.Serializer):
    not_imple = serializers.IntegerField()


class RecommendSerializer(serializers.Serializer):
    not_imple = serializers.IntegerField()

