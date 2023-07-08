from rest_framework import serializers


class StackDietSerializer(serializers.Serializer):
    military_number = serializers.ListField(default=[
        "6335", "2171", "8623", "5322", "6282", "7369", "5021", "8902", 
        "3296", "6176", "7652", "1570", "7162", "2291", "2621", "3007", 
        "5397", "1862", "6685", "5861", "7296",
        "3389", "1691", "9030", "1968", "3182", "2136"
    ])


class GetDietSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class GetPXFoodSerializer(serializers.Serializer):
    name = serializers.CharField(help_text='찾고자 하는 PX 식품 이름', max_length=60, default='라면')


class RecommendSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)


class SetTakenFoodSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    food = serializers.CharField(help_text='음식이름', max_length=60)


class DelTakenFoodSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    food = serializers.CharField(help_text='음식이름', max_length=60)


class GetTakenFoodSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    

class GetPXFoodListSerializer(serializers.Serializer):
    begin = serializers.IntegerField(default=0)
    end = serializers.IntegerField(default=10)


class GetRecommendPXFoodListSerializer(serializers.Serializer):
    military_serial_number = serializers.CharField(help_text='군번', max_length=15)
    begin = serializers.IntegerField(default=0)
    end = serializers.IntegerField(default=10)


class RecommendSuccessSerializer(serializers.Serializer):
    pxfoods = serializers.ListField(help_text='추천 PX 식품')


class GetPXFoodSuccessSerializer(serializers.Serializer):
    pxfoods = serializers.ListField(help_text='검색 PX 식품 리스트')


class GetRecommendPXFoodListSuccessSerializer(serializers.Serializer):
    pxfoods = serializers.ListField(help_text='인덱스 기준 추천 PX 식품 리스트')


class GetPXFoodListSuccessSerializer(serializers.Serializer):
    pxfoods = serializers.ListField(help_text='인덱스 기준 PX 식품 리스트')


class GetDietSuccessSerializer(serializers.Serializer):
    breakfast = serializers.ListField(help_text='아침 식단')
    lunch = serializers.ListField(help_text='점심 식단')
    dinner = serializers.ListField(help_text='저녁 식단')


class StackSuccessSerializer(serializers.Serializer):
    name = serializers.CharField(help_text='식단표 크롤링 성공', max_length=60)


class SetTakenFoodSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='먹은 음식 갱신 성공', max_length=60)


class GetTakenFoodSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='''{
        "pxfood": [],
        "diet": []
    }''', max_length=60)
