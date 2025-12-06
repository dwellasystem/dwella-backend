from django.urls import path
from .views import (
    MonthlyBillListCreateView, 
    MonthlyBillDetailView, 
    MonthlyBillStatsView, 
    MonthlyBillSummaryView, 
    UnitStatusSummaryView, 
    MonthlyBillListView,
    OverdueUserSummaryView,
    UserYearlyBillSummaryView,
    UserYearlyPaymentBreakdownView,
    FinancialReportsView,
    FinancialReportExportView,
    FinancialReportsView,
    UserFinancialComparisonView,
    UserFinancialReportExportView,
    PaidBillsExcelExportView,
    PaidBillsFilterOptionsView,
    ExpenseReflectionAPIView,
    YearlyExpenseAPIView,
    MonthlyExpenseAPIView
    )

urlpatterns = [
    path("bills/paginated", MonthlyBillListCreateView.as_view(), name="bill-list-create"),
    path('bills/', MonthlyBillListView.as_view(), name='bill-list'),
    path("bills/<int:pk>/", MonthlyBillDetailView.as_view(), name="bill-detail"),
    # path("bills/stats/", MonthlyBillStatsView.as_view(), name="bill-stats"),  # ✅ new endpoint
    path('bills/stats/', MonthlyBillStatsView.as_view(), name='bill-stats'),
    path('bills/summary/', MonthlyBillSummaryView.as_view(), name='bill-summary'),
    path('unit-status-summary/', UnitStatusSummaryView.as_view(), name='unit-status-summary'),
    path('overdues/', OverdueUserSummaryView.as_view(), name='overdues-accounts'),
    path('bills/yearly-summary/<int:user_id>/', UserYearlyPaymentBreakdownView.as_view()),
    # path('bills/financial-reports/', FinancialReportsView.as_view(), name='financial-reports'),
    path('bills/financial-reports/export/', FinancialReportExportView.as_view(), name='financial-reports-export'),

     # User-specific Financial Reports
    path('bills/financial-reports/user/<int:user_id>/', FinancialReportsView.as_view(), name='user-financial-reports'),
    path('bills/financial-reports/user-comparison/', UserFinancialComparisonView.as_view(), name='user-financial-comparison'),
    path('bills/financial-reports/user/<int:user_id>/export/', UserFinancialReportExportView.as_view(), name='user-financial-reports-export'),

    path('bills/export/paid-bills/excel/', PaidBillsExcelExportView.as_view(), name='export-paid-bills-excel'),
    path('bills/export/paid-bills/options/', PaidBillsFilterOptionsView.as_view(), name='paid-bills-options'),

    path('bills/expense-reflection/', ExpenseReflectionAPIView.as_view(), name='expense-reflection'),
    path('bills/expense-reflection/yearly/', YearlyExpenseAPIView.as_view(), name='yearly-expense'),
    path('bills/expense-reflection/monthly/<int:year>/', MonthlyExpenseAPIView.as_view(), name='monthly-expense'),
    
]