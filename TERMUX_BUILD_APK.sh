#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

echo "=============================================="
echo " Altabuki Pay - Termux APK Builder"
echo "=============================================="

if ! command -v python >/dev/null 2>&1; then
  echo "Python غير مثبت. نفذ: pkg install python -y"
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m py_compile main.py
find screens owner admin services -type f -name '*.py' -print0 | xargs -0 -r python -m py_compile

echo "فحص Python: OK"

echo "بدء بناء APK..."

if ! command -v flet >/dev/null 2>&1; then
  echo "أمر flet غير موجود بعد تثبيت الحزمة. حاول: python -m pip install flet"
  exit 1
fi

mkdir -p dist
flet build apk

APK=""
for p in build/app/outputs/flutter-apk/app-release.apk build/apk/app-release.apk build/app/outputs/flutter-apk/app-debug.apk; do
  if [ -f "$p" ]; then APK="$p"; break; fi
done

if [ -n "$APK" ]; then
  cp "$APK" dist/altabuki_pay.apk
  echo "=============================================="
  echo "تم إنشاء APK:"
  echo "$(pwd)/dist/altabuki_pay.apk"
  echo "=============================================="
else
  echo "انتهى أمر البناء، لكن لم يتم العثور على APK في المسارات المتوقعة."
  echo "افحص مجلد build/ وابحث عن *.apk"
  exit 2
fi
