import flet as ft
from services.user_manager import register_user


def register_view(page, on_back=None):
    name = ft.TextField(label='الاسم الكامل', prefix_icon=ft.icons.PERSON_OUTLINE, text_align=ft.TextAlign.RIGHT)
    phone = ft.TextField(label='رقم الهاتف / الحساب', prefix_icon=ft.icons.PHONE, keyboard_type=ft.KeyboardType.PHONE, text_align=ft.TextAlign.RIGHT)
    password = ft.TextField(label='كلمة المرور', prefix_icon=ft.icons.LOCK_OUTLINE, password=True, can_reveal_password=True, text_align=ft.TextAlign.RIGHT)
    confirm = ft.TextField(label='تأكيد كلمة المرور', prefix_icon=ft.icons.LOCK_OUTLINE, password=True, can_reveal_password=True, text_align=ft.TextAlign.RIGHT)
    docs = {'front': None, 'back': None, 'passport': None}
    msg = ft.Text('', text_align=ft.TextAlign.CENTER)

    def pick_doc(kind, title):
        picker = ft.FilePicker()
        def done(e):
            if e.files:
                docs[kind] = e.files[0].path
                labels[kind].value = '✓ ' + e.files[0].name
                page.update()
        picker.on_result = done
        page.overlay.append(picker)
        picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)

    labels = {k: ft.Text('لم يتم اختيار صورة', size=12, color=ft.colors.GREY_600) for k in docs}
    def doc_card(kind, title, icon):
        return ft.Container(border_radius=16, padding=14, bgcolor=ft.colors.GREY_100, content=ft.Row([ft.Icon(icon, color=ft.colors.INDIGO_500), ft.Column([ft.Text(title, weight=ft.FontWeight.BOLD), labels[kind]], expand=True), ft.OutlinedButton('اختيار', on_click=lambda e: pick_doc(kind,title))]))

    def submit(e):
        msg.value=''
        if password.value != confirm.value:
            msg.value='كلمتا المرور غير متطابقتين'; page.update(); return
        if not all(docs.values()):
            msg.value='يرجى تحميل صور البطاقة الأمامية والخلفية والجواز'; page.update(); return
        try:
            register_user(name.value, phone.value, password.value, id_image=docs['front'], id_front_image=docs['front'], id_back_image=docs['back'], passport_image=docs['passport'])
            msg.value='تم إرسال طلب التسجيل بنجاح. الحساب بانتظار مراجعة الإدارة.'
            page.update()
        except Exception as ex:
            msg.value=str(ex); page.update()

    return ft.View('/register', [ft.Container(expand=True, padding=24, content=ft.Column([ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: on_back() if on_back else None)], alignment=ft.MainAxisAlignment.START), ft.Text('إنشاء حساب جديد', size=30, weight=ft.FontWeight.BOLD), ft.Text('أدخل بياناتك وارفع الوثائق المطلوبة', color=ft.colors.GREY_600), name, phone, password, confirm, ft.Text('الوثائق المطلوبة', size=18, weight=ft.FontWeight.BOLD), doc_card('front','البطاقة الشخصية — الأمام',ft.icons.BADGE_OUTLINED), doc_card('back','البطاقة الشخصية — الخلف',ft.icons.BADGE_OUTLINED), doc_card('passport','جواز السفر',ft.icons.DESCRIPTION_OUTLINED), ft.ElevatedButton('إرسال طلب التسجيل', icon=ft.icons.CHECK_CIRCLE_OUTLINE, height=50, on_click=submit), msg], scroll=ft.ScrollMode.AUTO))])
