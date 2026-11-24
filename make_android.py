#!/usr/bin/env python3
"""Generates the Android (WebView) project from index.html. Run from repo root."""
import os, re, base64, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "android-project")
shutil.rmtree(OUT, ignore_errors=True)

def w(path, text, binary=False):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(text)

# ---------- patch web app for Android bridge ----------
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
def rep(a, b):
    global html
    assert html.count(a) == 1, "patch anchor not found: " + a[:50]
    html = html.replace(a, b)

rep("function downloadFile(f){",
"""function downloadFile(f){
  if(window.AndroidBridge){const r=new FileReader();r.onload=()=>{try{AndroidBridge.saveFile(f.name,f.type,String(r.result).split(',')[1])}catch(e){toast('সেভ হয়নি')}};r.readAsDataURL(f.blob);return}""")
rep("async function shareOut(){\n  if(!S.out)return;",
"""async function shareOut(){
  if(!S.out)return;
  if(window.AndroidBridge){
    const rd=b=>new Promise(res=>{const r=new FileReader();r.onload=()=>res(String(r.result).split(',')[1]);r.readAsDataURL(b)});
    AndroidBridge.shareBegin();
    for(const f of S.out.files)AndroidBridge.cacheFile(f.name,f.type,await rd(f.blob));
    AndroidBridge.shareCommit();return;
  }""")
rep("if('serviceWorker' in navigator&&", "if(!window.AndroidBridge&&'serviceWorker' in navigator&&")
w("app/src/main/assets/index.html", html)
w("app/src/main/res/mipmap-xxhdpi/ic_launcher.png", open(os.path.join(ROOT, "icon-192.png"), "rb").read(), True)
w("app/src/main/res/mipmap-xxxhdpi/ic_launcher.png", open(os.path.join(ROOT, "icon-192.png"), "rb").read(), True)

KS_B64 = "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"

# ---------- gradle ----------
w("settings.gradle", """pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "Scanner"
include ':app'
""")
w("build.gradle", "plugins { id 'com.android.application' version '8.5.2' apply false }\n")
w("gradle.properties", "org.gradle.jvmargs=-Xmx2g\nandroid.useAndroidX=true\n")
w("app/release.keystore", base64.b64decode(KS_B64), True)
w("app/build.gradle", """plugins { id 'com.android.application' }
android {
    namespace 'com.sojib.scanner'
    compileSdk 34
    defaultConfig {
        applicationId 'com.sojib.scanner'
        minSdk 29
        targetSdk 34
        versionCode 1
        versionName '1.0'
    }
    signingConfigs {
        release {
            storeFile file('release.keystore')
            storePassword 'scanner123'
            keyAlias 'scanner'
            keyPassword 'scanner123'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
dependencies {
    implementation 'androidx.webkit:webkit:1.11.0'
    implementation 'androidx.core:core:1.13.1'
}
""")

# ---------- manifest & resources ----------
w("app/src/main/AndroidManifest.xml", """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <application
        android:label="স্ক্যানার"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="false"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|density"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.sojib.scanner.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
""")
w("app/src/main/res/xml/file_paths.xml", """<?xml version="1.0" encoding="utf-8"?>
<paths><cache-path name="share" path="share/" /></paths>
""")

# ---------- activity ----------
w("app/src/main/java/com/sojib/scanner/MainActivity.java", r"""package com.sojib.scanner;

import android.Manifest;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.core.content.FileProvider;
import androidx.webkit.WebViewAssetLoader;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.ArrayList;

public class MainActivity extends Activity {
    private static final int REQ_FILE = 1, REQ_CAM = 2;
    private WebView web;
    private ValueCallback<Uri[]> fileCb;
    private PermissionRequest pendingPerm;
    private final ArrayList<File> shareFiles = new ArrayList<>();
    private final ArrayList<String> shareMimes = new ArrayList<>();

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                return loader.shouldInterceptRequest(r.getUrl());
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                            request.grant(request.getResources());
                        } else {
                            pendingPerm = request;
                            requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_CAM);
                        }
                    }
                });
            }

            @Override
            public boolean onShowFileChooser(WebView w, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (fileCb != null) fileCb.onReceiveValue(null);
                fileCb = cb;
                try {
                    startActivityForResult(p.createIntent(), REQ_FILE);
                } catch (Exception e) {
                    fileCb = null;
                    return false;
                }
                return true;
            }
        });
        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        web.loadUrl("https://appassets.androidplatform.net/assets/index.html");
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] res) {
        if (code == REQ_CAM && pendingPerm != null) {
            if (res.length > 0 && res[0] == PackageManager.PERMISSION_GRANTED) {
                pendingPerm.grant(pendingPerm.getResources());
            } else {
                pendingPerm.deny();
            }
            pendingPerm = null;
        }
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_FILE && fileCb != null) {
            fileCb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCb = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else finish();
    }

    private void toast(final String m) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, m, Toast.LENGTH_LONG).show();
            }
        });
    }

    private class Bridge {
        @JavascriptInterface
        public void saveFile(String name, String mime, String b64) {
            try {
                byte[] data = Base64.decode(b64, Base64.DEFAULT);
                ContentValues v = new ContentValues();
                v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
                v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                OutputStream os = getContentResolver().openOutputStream(u);
                os.write(data);
                os.close();
                toast("Downloads ফোল্ডারে সেভ হয়েছে: " + name);
            } catch (Exception e) {
                toast("সেভ হয়নি: " + e.getMessage());
            }
        }

        @JavascriptInterface
        public void shareBegin() {
            shareFiles.clear();
            shareMimes.clear();
            File dir = new File(getCacheDir(), "share");
            File[] old = dir.listFiles();
            if (old != null) for (File f : old) f.delete();
        }

        @JavascriptInterface
        public void cacheFile(String name, String mime, String b64) {
            try {
                File dir = new File(getCacheDir(), "share");
                dir.mkdirs();
                File f = new File(dir, name.replace("/", "_"));
                FileOutputStream os = new FileOutputStream(f);
                os.write(Base64.decode(b64, Base64.DEFAULT));
                os.close();
                shareFiles.add(f);
                shareMimes.add(mime);
            } catch (Exception e) {
                toast("শেয়ার ফাইল তৈরি হয়নি: " + e.getMessage());
            }
        }

        @JavascriptInterface
        public void shareCommit() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (shareFiles.isEmpty()) return;
                    ArrayList<Uri> uris = new ArrayList<>();
                    for (File f : shareFiles)
                        uris.add(FileProvider.getUriForFile(MainActivity.this, "com.sojib.scanner.fileprovider", f));
                    Intent i;
                    if (uris.size() == 1) {
                        i = new Intent(Intent.ACTION_SEND);
                        i.putExtra(Intent.EXTRA_STREAM, uris.get(0));
                    } else {
                        i = new Intent(Intent.ACTION_SEND_MULTIPLE);
                        i.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris);
                    }
                    i.setType(shareMimes.get(0));
                    i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(Intent.createChooser(i, "শেয়ার করুন"));
                }
            });
        }
    }
}
""")
print("OK: android-project generated")
