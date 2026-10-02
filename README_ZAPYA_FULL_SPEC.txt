التبوكي باي — حزمة Zapya للمشروع والمواصفات
إصدار 2026-10-01

هذه الحزمة تحتوي على:
1) نسخة المشروع المرجعية قبل التطوير.
2) PROJECT_BASELINE.md إن كان موجودًا.
3) PROJECT_FULL_SPEC.md — جميع المواصفات والتفاصيل التي تم توثيقها.
4) سكربتات تشغيل/بناء Termux الموجودة في المشروع.

فتح المشروع في Termux:
cd ~/altabuki_pay_baseline/altabuki_pay_baseline_2026-10-01

تشغيل الويب:
flet run --web main.py

فحص ملفات Python:
python -m compileall -q .

مهم:
المواصفات الموجودة في PROJECT_FULL_SPEC.md تصف ما نريد الوصول إليه، وليست ادعاءً بأن كل شيء مطبق حاليًا.
