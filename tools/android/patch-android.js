/* Chỉnh dự án Android do Capacitor sinh ra: xoay ngang, toàn màn hình, số phiên bản.
   Chạy trong thư mục build/ sau `npx cap add android`. Dùng: node patch-android.js <versionCode> */
const fs = require('fs');
const code = parseInt(process.argv[2] || '1', 10) || 1;
const man = 'android/app/src/main/AndroidManifest.xml';
let m = fs.readFileSync(man, 'utf8');
if (!m.includes('screenOrientation')) m = m.replace('<activity', '<activity android:screenOrientation="sensorLandscape"');
fs.writeFileSync(man, m);
const sty = 'android/app/src/main/res/values/styles.xml';
let s = fs.readFileSync(sty, 'utf8');
if (!s.includes('windowFullscreen')) s = s.replace(/(<style name="AppTheme\.NoActionBar"[^>]*>)/, '$1\n        <item name="android:windowFullscreen">true</item>\n        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>');
fs.writeFileSync(sty, s);
const gr = 'android/app/build.gradle';
let g = fs.readFileSync(gr, 'utf8');
g = g.replace(/versionCode \d+/, 'versionCode ' + code).replace(/versionName "[^"]*"/, 'versionName "1.0.' + code + '"');
fs.writeFileSync(gr, g);
console.log('Đã chỉnh Android: xoay ngang, toàn màn hình, phiên bản 1.0.' + code);
