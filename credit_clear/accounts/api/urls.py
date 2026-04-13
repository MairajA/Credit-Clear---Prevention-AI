from django.urls import path

from .views import AccountLinkCompleteView
from .views import AccountLinkInitiateView
from .views import AccountRefreshView
from .views import AddBillView
from .views import AnalysisStatusView
from .views import ConfirmCardsView
from .views import InstitutionListView
from .views import LinkedAccountDetailView
from .views import LinkedAccountListView
from .views import ManualAccountCreateView
from .views import PaymentDueListView
from .views import PaymentDueOverdueView
from .views import ScanResultsView
from .views import SkipBillsView
from .views import TransactionListView

app_name = "accounts_api"

urlpatterns = [
    # Institutions
    path("institutions/", InstitutionListView.as_view(), name="institution_list"),
    # Account linking
    path("link/initiate/", AccountLinkInitiateView.as_view(), name="link_initiate"),
    path("link/complete/", AccountLinkCompleteView.as_view(), name="link_complete"),
    # Linked accounts
    path("linked/", LinkedAccountListView.as_view(), name="linked_list"),
    path("linked/manual/", ManualAccountCreateView.as_view(), name="manual_create"),
    path("linked/<int:pk>/", LinkedAccountDetailView.as_view(), name="linked_detail"),
    path("linked/<int:pk>/refresh/", AccountRefreshView.as_view(), name="linked_refresh"),
    # Cards confirmation
    path("cards/confirm/", ConfirmCardsView.as_view(), name="cards_confirm"),
    # Bills
    path("bills/add/", AddBillView.as_view(), name="bills_add"),
    path("bills/skip/", SkipBillsView.as_view(), name="bills_skip"),
    # Transactions
    path("transactions/", TransactionListView.as_view(), name="transaction_list"),
    # Payment dues
    path("payment-dues/", PaymentDueListView.as_view(), name="payment_due_list"),
    path("payment-dues/overdue/", PaymentDueOverdueView.as_view(), name="payment_due_overdue"),
    # Analysis & scan
    path("analysis/status/", AnalysisStatusView.as_view(), name="analysis_status"),
    path("scan-results/", ScanResultsView.as_view(), name="scan_results"),
]
