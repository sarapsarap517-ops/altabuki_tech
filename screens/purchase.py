import flet as ft
from services.package_manager import get_package
from services.purchase_manager import calculate_purchase,purchase_cards

def purchase_view(page,current_user,network_id,package_id,navigate=None):
    pkg=get_package(package_id)
    if not pkg: return ft.View('/purchase',[ft.Text('الباقة غير موجودة')])
    qty=ft.TextField(label='الكمية',value='1',keyboard_type=ft.KeyboardType.NUMBER,text_align=ft.TextAlign.CENTER)
    beneficiary=ft.TextField(label='رقم هاتف العميل المستفيد',keyboard_type=ft.KeyboardType.PHONE,text_align=ft.TextAlign.RIGHT)
    summary=ft.Column(spacing=6); msg=ft.Text('')
    def calc(e=None):
        try:
            c=calculate_purchase(package_id,int(qty.value or 1),network_id); summary.controls=[ft.Text(f"السعر: {c['unit_price']:,.0f} ريال"),ft.Text(f"الكمية: {c['quantity']}"),ft.Text(f"العمولة: {c['commission']:,.0f} ريال ({c['commission_percent']:g}%)"),ft.Text(f"الإجمالي: {c['total_amount']:,.0f} ريال",size=20,weight=ft.FontWeight.BOLD)]; summary.update()
        except Exception as ex: msg.value=str(ex); summary.update()
    def buy(e):
        try:
            result=purchase_cards(current_user['user_id'],beneficiary.value,network_id,package_id,int(qty.value or 1)); msg.value=f"تم الشراء بنجاح. رقم العملية: {result['transaction']['transaction_id']}" if isinstance(result.get('transaction'),dict) else 'تم الشراء بنجاح'; page.update()
        except Exception as ex: msg.value=str(ex); page.update()
    qty.on_change=calc; calc()
    return ft.View('/purchase',[ft.AppBar(title=ft.Text('تأكيد الطلب'),leading=ft.IconButton(ft.icons.ARROW_BACK,on_click=lambda e:navigate('network_details',network_id=network_id) if navigate else None)),ft.Container(padding=20,content=ft.Column([ft.Container(padding=18,border_radius=20,bgcolor=ft.colors.WHITE,content=ft.Column([ft.Text(str(pkg.get('name','الباقة')),size=22,weight=ft.FontWeight.BOLD),ft.Text(f"الفئة: {pkg.get('denomination','—')}"),beneficiary,qty,summary],spacing=12)),ft.ElevatedButton('شراء الآن',height=52,icon=ft.icons.SHOPPING_CART,on_click=buy),msg]))])
