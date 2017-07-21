from rest_framework import serializers
from api.models import Snippet
from django.contrib.auth.models import User

'''class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=20)

    def create(self, validated_data):
        """
        Create and return
        """
        return Snippet.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        update
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
'''

class SnippetSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    # owner = serializers.RE(source='owner')

    class Meta:
        model = Snippet
        fields = ('id', 'title', 'description', 'owner')

class UserSerializer(serializers.ModelSerializer):

    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'snippets')
