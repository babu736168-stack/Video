package com.babu.voiceover

import android.content.Context
import android.net.Uri
import java.io.File
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.zip.ZipInputStream

/** Downloads (or imports) the offline Vosk Hindi speech model once, and finds it on disk. */
class ModelManager(private val ctx: Context) {
    companion object {
        const val MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip"
        const val MODEL_SIZE_MB = 42
    }

    private val root = File(ctx.filesDir, "vosk-hi")

    /** The folder that contains am/, conf/, graph/ ... or null if not installed yet. */
    fun modelPath(): String? {
        if (!root.exists()) return null
        if (File(root, "am").isDirectory) return root.absolutePath
        return root.listFiles()?.firstOrNull { File(it, "am").isDirectory }?.absolutePath
    }

    fun isReady() = modelPath() != null

    fun download(progress: (Int) -> Unit) {
        var url = URL(MODEL_URL)
        var conn: HttpURLConnection
        var redirects = 0
        while (true) {
            conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 20000; conn.readTimeout = 30000
            conn.instanceFollowRedirects = false
            val code = conn.responseCode
            if (code in 300..399 && redirects++ < 5) { url = URL(url, conn.getHeaderField("Location")); conn.disconnect(); continue }
            if (code != 200) throw IllegalStateException("Download failed (HTTP $code)")
            break
        }
        val total = conn.contentLengthLong.takeIf { it > 0 } ?: (MODEL_SIZE_MB * 1024L * 1024L)
        val tmp = File(ctx.cacheDir, "model.zip")
        conn.inputStream.use { inp ->
            tmp.outputStream().use { out ->
                val buf = ByteArray(64 * 1024); var done = 0L; var n: Int
                while (inp.read(buf).also { n = it } > 0) {
                    out.write(buf, 0, n); done += n
                    progress((done * 100 / total).toInt().coerceIn(0, 99))
                }
            }
        }
        tmp.inputStream().use { unzip(it) }
        tmp.delete()
        progress(100)
    }

    /** For when the download is blocked: the user picks the model .zip they downloaded in a browser. */
    fun import(uri: Uri) {
        ctx.contentResolver.openInputStream(uri)!!.use { unzip(it) }
        if (!isReady()) throw IllegalStateException("That zip does not contain a Vosk model")
    }

    private fun unzip(input: InputStream) {
        val staging = File(ctx.filesDir, "vosk-hi.tmp")
        staging.deleteRecursively(); staging.mkdirs()
        ZipInputStream(input.buffered()).use { zin ->
            var e = zin.nextEntry
            while (e != null) {
                val f = File(staging, e.name)
                if (!f.canonicalPath.startsWith(staging.canonicalPath + File.separator)) throw SecurityException("Bad zip entry")
                if (e.isDirectory) f.mkdirs() else { f.parentFile?.mkdirs(); f.outputStream().use { zin.copyTo(it) } }
                e = zin.nextEntry
            }
        }
        root.deleteRecursively()
        staging.renameTo(root)
    }
}
