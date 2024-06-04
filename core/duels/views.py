from .models import Duels, Maps
from .serializers import DuelsSerializer, MapsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json


class DuelsPagination(PageNumberPagination):
    page_size = 12


class OpenDuels(APIView):
    pagination_class = DuelsPagination

    @swagger_auto_schema(
        operation_description="Получение списка дуэлей",
        manual_parameters=[
            openapi.Parameter('min_bet', openapi.IN_QUERY, description="Minimum bet", type=openapi.TYPE_INTEGER),
            openapi.Parameter('max_bet', openapi.IN_QUERY, description="Maximum bet", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sorting', openapi.IN_QUERY, description="Sort by bet (asc/desc)",
                              type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        min_bet = request.query_params.get('min_bet', None)
        max_bet = request.query_params.get('max_bet', None)
        sorting = request.query_params.get('sorting', None)

        duels = Duels.objects.filter(status='open')

        if min_bet is not None:
            duels = duels.filter(bet__gte=min_bet)
        if max_bet is not None:
            duels = duels.filter(bet__lte=max_bet)
        if sorting is not None:
            if sorting.lower() == 'asc':
                duels = duels.order_by('bet')
            elif sorting.lower() == 'desc':
                duels = duels.order_by('-bet')

        paginator = DuelsPagination()
        page = paginator.paginate_queryset(duels, request)
        serializer = DuelsSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class CompletedDuelsCount(APIView):
    def get(self, request):
        duels_count = Duels.objects.filter(status='completed').count()
        return Response(duels_count, status=status.HTTP_200_OK)


class AllDuelsByToken(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        duels = Duels.objects.filter(Q(winner=request.user) | Q(player_1=request.user) | Q(player_2=request.user))
        serializer = DuelsSerializer(duels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateDuel(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def validation_duel(self, data) -> dict:
        response_data = {}
        bet = data.get('bet')
        map_name = data.get('map_name')
        player_1 = data.get('player_1')

        if bet is None:
            response_data = {'error': 'Bet is a required field.'}
            raise Exception('Bet is a required field.')
        else:
            bet = int(bet)
            if bet > player_1.balance:
                response_data = {'error': 'You do not have enough balance.'}

        if map_name is None:
            response_data = {'error': 'Map name is a required field.'}

        if player_1.balance < bet:
            response_data = {'error': 'You do not have enough balance.'}

        if player_1.leaves >= 3:
            response_data = {'error': 'You have reached the maximum number of leaves.'}

        return response_data

    @swagger_auto_schema(
        operation_description="Создание нового дуэля",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'bet': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bet amount'),
                'map_name': openapi.Schema(type=openapi.TYPE_STRING, description='Map name'),
                'date': openapi.Schema(type=openapi.TYPE_STRING, description='Date of the duel'),
                'time': openapi.Schema(type=openapi.TYPE_STRING, description='Time of the duel'),
                'time_zone': openapi.Schema(type=openapi.TYPE_STRING, description='Time zone of the duel'),
            }
        ),
        responses={201: 'Duel created successfully', 400: 'Invalid input'}
    )
    def post(self, request):
        response_data = {'error': 'An error occurred.'}
        response_status = status.HTTP_201_CREATED

        try:
            duel_dict = {
                'player_1': request.user,
                'bet': request.data.get('bet'),
                'map_name': Maps.objects.filter(name=request.data.get('map_name')).first(),
                'date': request.data.get('date'),
                'time': request.data.get('time'),
                'time_zone': request.data.get('time_zone')
            }

            response_data = self.validation_duel(duel_dict)
            if 'error' in response_data:
                raise Exception(response_data['error'])

            duel = Duels.objects.create(**duel_dict, player_1_bet=duel_dict['bet'])
            duel.player_1.balance -= int(duel.bet)
            duel.player_1.save()

            response_data = {'message': 'Duel created successfully.', 'duel_id': duel.id}
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
        finally:
            return Response(response_data, status=response_status)


class AllMaps(APIView):
    def get(self, request):
        maps = Maps.objects.all()
        serializer = MapsSerializer(maps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DuelContesting(APIView):
    @swagger_auto_schema(
        operation_description="Перевести дуэль в статус 'contestining'",

        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'duel_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the duel')
            }
        ),
        responses={200: 'Duel is contesting', 404: 'Duel not found'}
    )
    def post(self, request):
        data = json.loads(request.data)
        duel = Duels.objects.filter(
            Q(player_1=request.user) | Q(player_2=request.user),
            id=data.get('duel_id'),
            status='contesting',
        ).first()
        if duel is None:
            return Response({'error': 'Duel not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            duel.status = 'contesting'
            duel.save()
            return Response({'message': 'Duel is contesting.'}, status=status.HTTP_200_OK)


class DuelsByStatus(APIView):
    @swagger_auto_schema(
        operation_description="Получение дуэлей по статусу (и фильтрам)",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Status of the duel", type=openapi.TYPE_STRING,
                              enum=['open', 'completed', 'canceled', 'pending', 'started', 'contesting']),
            openapi.Parameter('min_bet', openapi.IN_QUERY, description="Minimum bet", type=openapi.TYPE_INTEGER),
            openapi.Parameter('max_bet', openapi.IN_QUERY, description="Maximum bet", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sorting', openapi.IN_QUERY, description="Sort by bet (asc/desc)",
                              type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        status_filter = request.query_params.get('status', None)
        min_bet = request.query_params.get('min_bet', None)
        max_bet = request.query_params.get('max_bet', None)
        sorting = request.query_params.get('sorting', None)

        if status_filter not in ['open', 'completed', 'canceled', 'pending', 'started', 'contesting']:
            return Response({'error': 'Invalid status filter.'}, status=status.HTTP_400_BAD_REQUEST)

        duels = Duels.objects.filter(status=status_filter)

        if min_bet is not None:
            duels = duels.filter(bet__gte=min_bet)
        if max_bet is not None:
            duels = duels.filter(bet__lte=max_bet)
        if sorting is not None:
            if sorting.lower() == 'asc':
                duels = duels.order_by('bet')
            elif sorting.lower() == 'desc':
                duels = duels.order_by('-bet')

        paginator = DuelsPagination()
        page = paginator.paginate_queryset(duels, request)
        serializer = DuelsSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
