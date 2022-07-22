from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer
from base.models import Room
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    # rooms = Room.objects.all()
    # serializer = RoomSerializer(rooms, many=True)
    # return Response(serializer.data)
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status_HTTP_200_CREATED)
        return Response(serializer.error, status.HTTP_400_BAD_REQUEST)

# Above serializer will retrieve room data or create new room if not found as soon as it enters in elif statement.

@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)