from datetime import date

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from circulation.models import Loan
from circulation.serializers import LoanSerializer, LoanReturnSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by("-id")
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set issued_by to current user's staff profile
        user = request.user
        staff = getattr(user, 'staff_profile', None)
        
        if not staff:
            return Response(
                {"detail": "User must have staff profile to issue books"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan = serializer.save(issued_by=staff)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        loan.status = Loan.Status.RETURNED
        loan.return_date = date.today()
        loan.save()
        return Response(LoanSerializer(loan).data)
