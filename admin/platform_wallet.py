import flet as ft
from services.platform_wallet import get_balance, credit, debit

def platform_wallet_view(page, admin_user_id=None):
    amount=ft.TextField(label='المبلغ',keyboard_type=ft.KeyboardType.NUMBER,text_align=ft.TextAlign.RIGHT)
    msg=ft.Text('')
    balance=ft.Text('',size=28,weight=ft.FontWeight.BOLD,color=ft.colors.INDIGO_600)
    def refresh(): balance.value=f'{get_balance():,.0f} ريال'; page.update()
    def action(kind):
        try:
            v=float(amount.value or 0)
            (credit if kind=='credit' else debit)(v, reason='تعديل إداري')
            msg.value='تم تحديث رصيد المنصة'; amount.value=''; refresh()
        except Exception as ex: msg.value=str(ex); page.update()
    refresh()
    return ft.Column([ft.Container(padding=20,border_radius=20,bgcolor=ft.colors.WHITE,content=ft.Column([ft.Text('رصيد المنصة',size=16),balance,amount,ft.Row([ft.ElevatedButton('إيداع',on_click=lambda e:action('credit')),ft.OutlinedButton('سحب',on_click=lambda e:action('debit'))])])),msg],scroll=ft.ScrollMode.AUTO)
