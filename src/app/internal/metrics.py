from prometheus_client import Counter, Gauge

USER_AMOUNT = Gauge("user_amount", "")

TRANSFER_AMOUNT = Gauge("transfer_amount", "")
TRANSFER_ERRORS = Counter("transfer_errors", "")

ACCOUNT_AMOUNT = Gauge("account_amount", "")
CARD_AMOUNT = Gauge("card_amount", "")
BALANCE_TOTAL = Gauge("balance_total", "")
