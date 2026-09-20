package com.cashflowtracking.cashflowtracking

import android.content.Context
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import org.json.JSONObject
import java.io.File
import java.io.FileWriter

class BankNotificationListener : NotificationListenerService() {

    override fun onListenerConnected() {
        super.onListenerConnected()
        Log.i("CashflowNotif", "BankNotificationListener connected! Scanning active notifications...")
        try {
            val activeNotifs = activeNotifications
            if (activeNotifs != null) {
                Log.i("CashflowNotif", "Active notifications count: ${activeNotifs.size}")
                for (sbn in activeNotifs) {
                    processNotification(sbn)
                }
            }
        } catch (e: Exception) {
            Log.e("CashflowNotif", "Error scanning active notifications", e)
        }
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return
        processNotification(sbn)
    }

    private fun processNotification(sbn: StatusBarNotification) {
        val notif = sbn.notification ?: return

        // 1. Skip group summaries (e.g. Gmail group summary notification that bundles multiple emails)
        val isGroupSummary = (notif.flags and android.app.Notification.FLAG_GROUP_SUMMARY) != 0
        if (isGroupSummary) {
            Log.d("CashflowNotif", "Skipping group summary notification from ${sbn.packageName}")
            return
        }

        val pkg = sbn.packageName ?: ""
        val lowerPkg = pkg.lowercase()
        val isTargetBank = lowerPkg.contains("sacombank") ||
                           lowerPkg.contains("cake") ||
                           lowerPkg.contains("momotransfer") ||
                           lowerPkg.contains("momo") ||
                           lowerPkg.contains("vcb") ||
                           lowerPkg.contains("vietcombank") ||
                           lowerPkg.contains("mbbank") ||
                           lowerPkg.contains("techcombank") ||
                           lowerPkg.contains("tpbank") ||
                           lowerPkg.contains("acb") ||
                           lowerPkg.contains("bidv") ||
                           lowerPkg.contains("vpbank")

        val isEmailOrSms = lowerPkg.contains("android.gm") ||
                           lowerPkg.contains("email") ||
                           lowerPkg.contains("mail") ||
                           lowerPkg.contains("outlook") ||
                           lowerPkg.contains("messaging") ||
                           lowerPkg.contains("mms")

        if (!isTargetBank && !isEmailOrSms) return

        val extras = notif.extras ?: return
        val title = extras.getCharSequence("android.title")?.toString() ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""
        val bigText = extras.getCharSequence("android.bigText")?.toString() ?: ""
        val fullText = if (bigText.isNotEmpty() && bigText.length > text.length) bigText else text

        if (isEmailOrSms) {
            val contentLower = "$title $fullText".lowercase()
            val hasBankKw = contentLower.contains("sacombank") ||
                            contentLower.contains("cake") ||
                            contentLower.contains("vietcombank") ||
                            contentLower.contains("vcb") ||
                            contentLower.contains("mbbank") ||
                            contentLower.contains("techcombank") ||
                            contentLower.contains("tpbank") ||
                            contentLower.contains("acb") ||
                            contentLower.contains("bidv") ||
                            contentLower.contains("vpbank") ||
                            contentLower.contains("biến động số dư") ||
                            contentLower.contains("thông báo giao dịch") ||
                            contentLower.contains("balance alert") ||
                            contentLower.contains("phát sinh")
            if (!hasBankKw) return
        }

        // 2. Deduplication using content-based fingerprint + 10-minute cooldown window
        val normalizedContent = "${pkg.lowercase()}|${title.trim().lowercase()}|${fullText.trim().lowercase()}"
        val contentHash = java.security.MessageDigest.getInstance("MD5")
            .digest(normalizedContent.toByteArray())
            .joinToString("") { "%02x".format(it) }

        val prefs = getSharedPreferences("cashflow_notif_keys", Context.MODE_PRIVATE)
        val lastSeen = prefs.getLong("hash_$contentHash", 0L)
        val now = System.currentTimeMillis()
        if (now - lastSeen < 600_000L) { // 10 minutes deduplication window
            Log.i("CashflowNotif", "Ignoring duplicate notification ($contentHash) within cooldown window")
            return
        }
        prefs.edit().putLong("hash_$contentHash", now).apply()

        Log.i("CashflowNotif", "Detected bank notification: [$pkg] $title: $fullText")

        try {
            // Write to app internal files dir
            val dir = applicationContext.filesDir
            val dataDir = File(dir, "data")
            val targetDir = if (dataDir.exists()) dataDir else dir
            val notifFile = File(targetDir, "incoming_notifications.jsonl")

            val json = JSONObject()
            json.put("package", pkg)
            json.put("title", title)
            json.put("text", fullText)
            json.put("time", sbn.postTime)
            json.put("id", sbn.id)

            FileWriter(notifFile, true).use { writer ->
                writer.append(json.toString()).append("\n")
            }
            Log.i("CashflowNotif", "Successfully queued bank notification to ${notifFile.absolutePath}")
        } catch (e: Exception) {
            Log.e("CashflowNotif", "Error saving notification", e)
        }
    }
}

