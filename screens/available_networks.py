import flet as ft
from services.network_manager import get_approved_networks
from services.user_manager import set_favorite_network

PRIMARY=ft.colors.INDIGO_600

def available_networks_view(page,current_user=None,navigate=None):
    user=current_user or getattr(page,'current_user',{}) or {}
    uid=user.get('user_id')
    search=ft.TextField(label='بحث باسم الشبكة أو رقمها', prefix_icon=ft.icons.SEARCH, text_align=ft.TextAlign.RIGHT)
    tabs=ft.Tabs(selected_index=0, animation_duration=250)
    body=ft.Column(spacing=12,scroll=ft.ScrollMode.AUTO,expand=True)
    favorites=set(user.get('favorite_network_ids',[]) or [])
    allnets=[]
    def save_fav(nid, value):
        try:
            set_favorite_network(uid, nid, value)
        except Exception:
            pass

    def render():
        q=(search.value or '').strip().lower(); body.controls.clear(); nets=[n for n in allnets if not q or q in str(n.get('network_name','')).lower() or q in str(n.get('network_id','')).lower()]
        if tabs.selected_index==1: nets=[n for n in nets if int(n.get('network_id',0)) in favorites]
        if not nets: body.controls.append(ft.Container(padding=40,content=ft.Column([ft.Icon(ft.icons.WIFI_FIND_OUTLINED,size=55,color=PRIMARY),ft.Text('لا توجد شبكات مطابقة',size=20,weight=ft.FontWeight.BOLD),ft.Text('جرّب تغيير البحث أو أضف الشبكة للمفضلة.')],horizontal_alignment=ft.CrossAxisAlignment.CENTER))); body.update(); return
        for n in nets:
            nid=int(n.get('network_id',0)); fav=nid in favorites
            def open_net(e,nid=nid): navigate('network_details',network_id=nid) if navigate else None
            def fav_click(e,nid=nid):
                
                if nid in favorites:
                    favorites.discard(nid); save_fav(nid, False)
                else:
                    favorites.add(nid); save_fav(nid, True)
                render()
            body.controls.append(ft.Container(padding=16,border_radius=20,bgcolor=ft.colors.WHITE,shadow=ft.BoxShadow(blur_radius=7,color=ft.colors.BLACK12),content=ft.Row([ft.Icon(ft.icons.WIFI,size=35,color=PRIMARY),ft.Column([ft.Text(str(n.get('network_name','بدون اسم')),size=18,weight=ft.FontWeight.BOLD),ft.Text(f"رقم الشبكة: {nid}"),ft.Text(f"📍 {n.get('area','غير محددة')}",color=ft.colors.GREY_700)],expand=True),ft.Column([ft.IconButton(ft.icons.FAVORITE if fav else ft.icons.FAVORITE_BORDER,on_click=fav_click),ft.OutlinedButton('الباقات',on_click=open_net)],horizontal_alignment=ft.CrossAxisAlignment.CENTER)])))
        body.update()
    def load(e=None):
        nonlocal allnets
        allnets=get_approved_networks(); render()
    search.on_change=lambda e: render()
    tabs.tabs=[ft.Tab(text='كل الشبكات'),ft.Tab(text='المفضلة')]; tabs.on_change=lambda e:render()
    load()
    return ft.View('/available-networks',[ft.AppBar(title=ft.Text('الشبكات المتاحة'),leading=ft.IconButton(ft.icons.ARROW_BACK,on_click=lambda e:navigate('home') if navigate else None),actions=[ft.IconButton(ft.icons.REFRESH,on_click=load)]),ft.Container(expand=True,padding=16,content=ft.Column([search,tabs,body],expand=True))])
