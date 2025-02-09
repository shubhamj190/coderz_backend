from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class BaseViewSet(viewsets.ModelViewSet):
    def get_throttles(self):
        if self.action in ['create', 'update', 'destroy']:
            self.throttle_scope = f'{self.basename}_write'
        return super().get_throttles()

    def handle_exception(self, exc):
        if isinstance(exc, Exception):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)