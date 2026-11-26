plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.babu.voiceover"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.babu.voiceover"
        minSdk = 29          // Android 10+
        targetSdk = 35
        versionCode = 6
        versionName = "1.4.1"
        ndk { abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86") }
    }

    signingConfigs {
        create("release") {
            storeFile = file("../keystore/voiceover-release.jks")
            storePassword = "voiceover123"
            keyAlias = "voiceover"
            keyPassword = "voiceover123"
            enableV1Signing = true   // maximum installer compatibility
            enableV2Signing = true
            enableV3Signing = true
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")
        }
    }
    packaging { jniLibs { useLegacyPackaging = true } }   // compressed native libs: accepted by every installer
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin { compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17) } }

dependencies {
    implementation("com.alphacephei:vosk-android:0.3.75")
    implementation("net.java.dev.jna:jna:5.18.1@aar")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
