# NOVELIX ProGuard Rules
# Capacitor WebView App — keep all WebView/JS bridge classes

# ─── Capacitor Core ───────────────────────────────────────────────────────────
-keep class com.getcapacitor.** { *; }
-keepclassmembers class com.getcapacitor.** { *; }
-dontwarn com.getcapacitor.**

# ─── WebView JavaScript Interface ─────────────────────────────────────────────
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# ─── AndroidX / AppCompat ─────────────────────────────────────────────────────
-keep class androidx.** { *; }
-dontwarn androidx.**

# ─── Splash Screen ────────────────────────────────────────────────────────────
-keep class androidx.core.splashscreen.** { *; }

# ─── OkHttp / Networking ──────────────────────────────────────────────────────
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }

# ─── Stack Traces (for crash debugging) ───────────────────────────────────────
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# ─── Enums ────────────────────────────────────────────────────────────────────
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# ─── Parcelable ───────────────────────────────────────────────────────────────
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# ─── R classes ────────────────────────────────────────────────────────────────
-keepclassmembers class **.R$* {
    public static <fields>;
}
