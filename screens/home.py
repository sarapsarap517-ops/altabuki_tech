import flet as ft
from services.wallet_manager import get_balance
from services.platform_wallet import get_balance as platform_balance

PRIMARY = ft.colors.INDIGO_600
BG = ft.colors.GREY_50

def _money(v): return f'{float(v):,.0f} ريال'

def home_view(page, current_user=None, navigate=None, logout=None):
    user=current_user or getattr(page,'current_user',{}) or {}
    uid=user.get('user_id'); role=user.get('role','customer'); name=user.get('name','مستخدم')
    balance = platform_balance() if role=='admin' else get_balance(uid)
    balance_visible={'v':True}
    balance_text=ft.Text(_money(balance), size=25, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    def toggle(e):
        balance_visible['v']=not balance_visible['v']; balance_text.value=_money(balance) if balance_visible['v'] else '••••••'; page.update()
    def nav(r,**kw):
        if navigate: navigate(r,**kw)
    def tile(icon,title,route):
        return ft.Container(width=150,height=105,padding=14,border_radius=18,bgcolor=ft.colors.WHITE,shadow=ft.BoxShadow(blur_radius=8,spread_radius=0,color=ft.colors.BLACK12),content=ft.Column([ft.Icon(icon,size=30,color=PRIMARY),ft.Text(title,weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),on_click=lambda e:nav(route))
    services=[(ft.icons.WIFI,'الشبكات المتاحة','networks'),(ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,'المحفظة','wallet'),(ft.icons.RECEIPT_LONG_OUTLINED,'كشف الحساب','accounting'),(ft.icons.INSERT_CHART_OUTLINED,'التقارير','reports'),(ft.icons.SETTINGS_OUTLINED,'الإعدادات','settings'),(ft.icons.STORE_OUTLINED,'معرض الشبكات','network_gallery')]
    if role=='admin': services += [(ft.icons.ADMIN_PANEL_SETTINGS,'لوحة الإدارة','admin')]
    if role=='network_owner': services += [(ft.icons.HUB_OUTLINED,'شبكاتي','my_networks')]
    return ft.View('/home',[ft.Container(expand=True,bgcolor=BG,padding=18,content=ft.Column([ft.Row([ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON),bgcolor=ft.colors.WHITE),ft.Column([ft.Text('مرحبًا بك',size=13,color=ft.colors.WHITE70),ft.Text(name,size=18,weight=ft.FontWeight.BOLD,color=ft.colors.WHITE)],spacing=0,expand=True),ft.IconButton(ft.icons.NOTIFICATIONS_NONE,color=ft.colors.WHITE),ft.IconButton(ft.icons.MORE_VERT,color=ft.colors.WHITE,on_click=lambda e:nav('settings'))],vertical_alignment=ft.CrossAxisAlignment.CENTER),ft.Container(padding=20,border_radius=24,bgcolor=PRIMARY,content=ft.Row([ft.Column([ft.Text('الرصيد المتاح',color=ft.colors.WHITE70),balance_text],expand=True),ft.IconButton(ft.icons.VISIBILITY,color=ft.colors.WHITE,on_click=toggle)])),ft.Text('الخدمات',size=21,weight=ft.FontWeight.BOLD),ft.Row([ft.Container(expand=True,content=ft.GridView(runs_count=2,max_extent=170,spacing=12,run_spacing=12,controls=[tile(*x) for x in services]))],expand=True)],scroll=ft.ScrollMode.AUTO))])
