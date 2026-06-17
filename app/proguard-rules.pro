# Rev J WebView / JavaScript bridge protection.
# Keep Android WebView JavaScript interfaces and methods used from bundled JavaScript.
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keep class com.ahmed.azkartv.MainActivity$ShareBridge { *; }
-keepclassmembers class com.ahmed.azkartv.MainActivity { *; }
-keepattributes *Annotation*,InnerClasses,EnclosingMethod
-dontwarn org.chromium.**
