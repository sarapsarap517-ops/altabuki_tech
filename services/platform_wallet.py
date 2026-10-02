from datetime import datetime
from services.storage import load_json, save_json

FILE = 'platform_wallet'

def _now(): return datetime.now().isoformat()

def _load():
    d = load_json(FILE)
    d.setdefault('wallet', {'balance': 0.0, 'updated_at': _now()})
    return d

def get_wallet(): return _load()['wallet']
def get_balance(): return float(get_wallet().get('balance', 0))

def credit(amount, reason='', transaction_id=None):
    amount=float(amount)
    if amount < 0: raise ValueError('المبلغ غير صحيح')
    d=_load(); w=d['wallet']; w['balance']=float(w.get('balance',0))+amount; w['updated_at']=_now()
    d.setdefault('ledger',[]).append({'type':'credit','amount':amount,'reason':reason,'transaction_id':transaction_id,'created_at':_now()})
    save_json(FILE,d); return w

def debit(amount, reason='', transaction_id=None):
    amount=float(amount)
    if amount <= 0: raise ValueError('المبلغ غير صحيح')
    d=_load(); w=d['wallet']; bal=float(w.get('balance',0))
    if bal < amount: raise ValueError('رصيد المنصة غير كافٍ')
    w['balance']=bal-amount; w['updated_at']=_now()
    d.setdefault('ledger',[]).append({'type':'debit','amount':amount,'reason':reason,'transaction_id':transaction_id,'created_at':_now()})
    save_json(FILE,d); return w
