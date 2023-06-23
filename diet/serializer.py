from rest_framework import serializers


class StackDietSerializer(serializers.Serializer):
    military_number = serializers.ListField(default=[
        "6335", "2171", "8623", "5322", "6282", "7369", "5021", "8902", 
        "3296", "6176", "7652", "1570", "7162", "2291", "2621", "3007", 
        "5397", "1862", "6685", "5861", "7296",
        "3389", "1691", "9030", "1968", "3182", "2136"
    ])


class GetDietSerializer(serializers.Serializer):
    military_number = serializers.IntegerField(default=6335)


class GetPXFoodSerializer(serializers.Serializer):
    name = serializers.CharField(help_text='찾고자 하는 PX 식품 이름', max_length=60, default='라면')


class RecommendSerializer(serializers.Serializer):
    not_imple = serializers.IntegerField()

