from rest_framework import serializers
import phonenumbers

COUNTRY_CHOICE = ("IN",)


class GenerateOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    country = serializers.ChoiceField(COUNTRY_CHOICE)

    def validate(self, attrs):
        if not phonenumbers.is_possible_number(
            phonenumbers.parse(attrs.get("phone"), attrs.get("country"))
        ):
            raise serializers.ValidationError({"phone": "Phone must be valid"})
        return attrs
