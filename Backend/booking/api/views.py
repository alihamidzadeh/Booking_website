from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_views(request):
    return Response({
        'hotel': reverse('hotel', request=request),
        'airplane': reverse('airplane', request=request),
        'train' : reverse('Train', request=request),
        # 'user': reverse('User', request=request),
    })
