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
        val pkg = sbn.packageName ?: ""
        val lowerPkg = pkg.lowercase()
        val isTarget = lowerPkg.contains("sacombank") ||
                       lowerPkg.contains("cake") ||
                       lowerPkg.contains("momotransfer") ||
                       lowerPkg.contains("momo") ||
                       lowerPkg.contains("vcb") ||
                       lowerPkg.contains("vietcombank") ||
                       lowerPkg.contains("mbbank")

        if (!isTarget) return

        val key = "${sbn.id}_${sbn.postTime}_$pkg"
        val prefs = getSharedPreferences("cashflow_notif_keys", Context.MODE_PRIVATE)
        if (prefs.getBoolean(key, false)) return
        prefs.edit().putBoolean(key, true).apply()

        val extras = sbn.notification?.extras ?: return
        val title = extras.getCharSequence("android.title")?.toString() ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""
        val bigText = extras.getCharSequence("android.bigText")?.toString() ?: ""
        val fullText = if (bigText.isNotEmpty() && bigText.length > text.length) bigText else text

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

            FileWriter(notifFile, true).use { writer ->
                writer.append(json.toString()).append("\n")
            }
            Log.i("CashflowNotif", "Successfully queued bank notification to ${notifFile.absolutePath}")
        } catch (e: Exception) {
            Log.e("CashflowNotif", "Error saving notification", e)
        }
    }
}

