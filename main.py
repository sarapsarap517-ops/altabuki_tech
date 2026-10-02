import flet as ft
from screens.login import login_view
from screens.register import register_view
from screens.home import home_view
from screens.networks import networks_view
from screens.available_networks import available_networks_view
from screens.network_details import network_details_view
from screens.wallet import wallet_view
from screens.accounting import accounting_view
from screens.reports import reports_view
from screens.account import account_view
from screens.settings import settings_view
from screens.purchase import purchase_view
from owner.my_networks import my_networks_view
from owner.add_network import add_network_view
from owner.packages import packages_view
from owner.cards import cards_view
from admin.users import admin_users_view
from admin.networks import admin_networks_view
from admin.reports import admin_reports_view
from admin.platform_wallet import platform_wallet_view

PRIMARY=ft.colors.INDIGO_600

def main(page: ft.Page):
    page.title='التبوكي باي'
    page.rtl=True
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=0
    page.bgcolor=ft.colors.GREY_50
    page.current_user=None

    def uid(): return (page.current_user or {}).get('user_id')
    def role(): return (page.current_user or {}).get('role')
    def show(view):
        page.views.clear(); page.views.append(view if isinstance(view,ft.View) else ft.View('/screen',[view])); page.update()
    def logout(): page.current_user=None; show_login()
    def show_login(): show(login_view(page,on_login=handle_login,on_register=show_register))
    def show_register(): show(register_view(page,on_back=show_login))
    def handle_login(user):
        page.current_user=user
        if user.get('role')=='admin': show_admin_home()
        elif user.get('role')=='network_owner': show_owner_home()
        else: show_client_home()
    def client_nav(r,**kw):
        if r=='home': show_client_home()
        elif r=='networks': show(available_networks_view(page,page.current_user,client_nav))
        elif r=='network_gallery': show(networks_view(page,page.current_user,client_nav))
        elif r=='network_details': show(network_details_view(page,kw.get('network_id'),page.current_user,client_nav))
        elif r=='purchase': show(purchase_view(page,page.current_user,kw.get('network_id'),kw.get('package_id'),client_nav))
        elif r=='wallet': show(wallet_view(page,page.current_user,client_nav))
        elif r=='accounting': show(accounting_view(page,page.current_user,client_nav))
        elif r=='reports': show(reports_view(page,page.current_user,client_nav))
        elif r=='account': show(account_view(page,page.current_user,client_nav,logout))
        elif r=='settings': show(settings_view(page,page.current_user,client_nav,logout))
    def show_client_home(): show(home_view(page,page.current_user,client_nav,logout))
    def owner_nav(r,**kw):
        if r in ('home','my_networks'): show_owner_home()
        elif r=='add_network': show(add_network_view(page,page.current_user,owner_nav))
        elif r=='packages': show(packages_view(page,kw.get('network_id'),page.current_user,owner_nav))
        elif r=='cards': show(cards_view(page,kw.get('package_id'),kw.get('network_id'),page.current_user,owner_nav))
        elif r=='network_details': show(network_details_view(page,kw.get('network_id'),page.current_user,owner_nav))
        elif r=='networks': show(available_networks_view(page,page.current_user,owner_nav))
        elif r=='network_gallery': show(networks_view(page,page.current_user,owner_nav))
    def show_owner_home(): show(my_networks_view(page,page.current_user,owner_nav,logout))
    def show_admin_home():
        bal=__import__('services.platform_wallet',fromlist=['get_balance']).get_balance()
        show(ft.View('/admin',[ft.AppBar(title=ft.Text('لوحة الإدارة'),actions=[ft.IconButton(ft.icons.LOGOUT,on_click=lambda e:logout())]),ft.Container(expand=True,padding=16,content=ft.Column([ft.Container(padding=20,border_radius=20,bgcolor=PRIMARY,content=ft.Column([ft.Text('رصيد المنصة',color=ft.colors.WHITE70),ft.Text(f'{bal:,.0f} ريال',size=28,weight=ft.FontWeight.BOLD,color=ft.colors.WHITE)])),ft.Row([ft.ElevatedButton('المستخدمون',on_click=lambda e:show_admin_users()),ft.ElevatedButton('الشبكات',on_click=lambda e:show_admin_networks())]),ft.Row([ft.ElevatedButton('رصيد المنصة',on_click=lambda e:show_platform_wallet()),ft.ElevatedButton('التقارير',on_click=lambda e:show_admin_reports())])],scroll=ft.ScrollMode.AUTO))]))
    def show_admin_users(): show(ft.Column([ft.TextButton('← لوحة الإدارة',on_click=lambda e:show_admin_home()),admin_users_view(page,uid())],expand=True))
    def show_admin_networks(): show(ft.Column([ft.TextButton('← لوحة الإدارة',on_click=lambda e:show_admin_home()),admin_networks_view(page,uid())],expand=True))
    def show_admin_reports(): show(ft.Column([ft.TextButton('← لوحة الإدارة',on_click=lambda e:show_admin_home()),admin_reports_view(page,uid())],expand=True))
    def show_platform_wallet(): show(ft.Column([ft.TextButton('← لوحة الإدارة',on_click=lambda e:show_admin_home()),platform_wallet_view(page,uid())],expand=True))
    show_login()

if __name__=='__main__': ft.app(target=main)
