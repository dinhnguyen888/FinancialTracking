package com.cashflowtracking.cashflowtracking

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import org.json.JSONObject
import java.io.File
import java.io.FileWriter

class BankNotificationListener : NotificationListenerService() {

    private val processedKeys = HashSet<String>()

    override fun onListenerConnected() {
        super.onListenerConnected()
        Log.e("CashflowNotif", "BankNotificationListener connected! Scanning active notifications...")
        try {
            val dir = applicationContext.filesDir
            val dataDir = File(dir, "data")
            if (!dataDir.exists()) dataDir.mkdirs()
            val extDir = applicationContext.getExternalFilesDir(null)

            val flagTargets = mutableListOf(
                File(dir, "notification_permission_enabled.flag"),
                File(dataDir, "notification_permission_enabled.flag")
            )
            if (extDir != null) {
                flagTargets.add(File(extDir, "notification_permission_enabled.flag"))
            }
            for (f in flagTargets) {
                try { f.createNewFile() } catch (e: Exception) {}
            }
        } catch (e: Exception) {
            // ignore
        }
        try {
            val activeNotifs = activeNotifications
            if (activeNotifs != null) {
                Log.e("CashflowNotif", "Active notifications count: ${activeNotifs.size}")
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

        // 1. Target bank & e-wallet apps in Vietnam
        val isBankApp = lowerPkg.contains("sacombank") ||
                       lowerPkg.contains("ewallet") ||
                       lowerPkg.contains("cake") ||
                       lowerPkg.contains("momotransfer") ||
                       lowerPkg.contains("momo") ||
                       lowerPkg.contains("vcb") ||
                       lowerPkg.contains("vietcombank") ||
                       lowerPkg.contains("vietinbank") ||
                       lowerPkg.contains("ipay") ||
                       lowerPkg.contains("bidv") ||
                       lowerPkg.contains("techcombank") ||
                       lowerPkg.contains("tcb") ||
                       lowerPkg.contains("tpbank") ||
                       lowerPkg.contains("tpb") ||
                       lowerPkg.contains("vpbank") ||
                       lowerPkg.contains("acb") ||
                       lowerPkg.contains("mbbank") ||
                       lowerPkg.contains("agribank") ||
                       lowerPkg.contains("zalopay") ||
                       lowerPkg.contains("shopeepay") ||
                       lowerPkg.contains("airpay") ||
                       lowerPkg.contains("viettelmoney") ||
                       lowerPkg.contains("vtpay") ||
                       lowerPkg.contains("timo") ||
                       lowerPkg.contains("hdbank") ||
                       lowerPkg.contains("ocb") ||
                       lowerPkg.contains("shb") ||
                       lowerPkg.contains("msb") ||
                       lowerPkg.contains("seabank") ||
                       lowerPkg.contains("vnpay")

        val isSmsApp = lowerPkg.contains("messaging") ||
                       lowerPkg.contains("mms") ||
                       lowerPkg.contains("message")

        val extras = sbn.notification?.extras ?: return
        val title = extras.getCharSequence("android.title")?.toString() ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""
        val bigText = extras.getCharSequence("android.bigText")?.toString() ?: ""
        val fullText = if (bigText.isNotEmpty() && bigText.length > text.length) bigText else text
        val combined = "$title $fullText".lowercase()

        // Financial keywords for SMS banking and unknown bank apps
        val hasFinancialKeywords = combined.contains("ps:") ||
                                   combined.contains("gd:") ||
                                   combined.contains("sd tk") ||
                                   combined.contains("số dư") ||
                                   combined.contains("so du") ||
                                   combined.contains("biến động") ||
                                   combined.contains("bien dong") ||
                                   combined.contains("vừa tăng") ||
                                   combined.contains("vừa giảm") ||
                                   combined.contains("vua tang") ||
                                   combined.contains("vua giam") ||
                                   combined.contains("nhận tiền") ||
                                   combined.contains("nhan tien") ||
                                   combined.contains("chuyển tiền") ||
                                   combined.contains("chuyen tien") ||
                                   combined.contains("chuyển khoản") ||
                                   combined.contains("chuyen khoan") ||
                                   combined.contains("thanh toán") ||
                                   combined.contains("thanh toan") ||
                                   combined.contains("napas") ||
                                   combined.contains("vnd") ||
                                   combined.contains("vnđ")

        // Only accept if:
        // - It's a recognized bank app OR
        // - It's an SMS or notification with explicit financial keywords
        if (!isBankApp && !hasFinancialKeywords) {
            return
        }

        val key = "${sbn.id}_${sbn.postTime}_$pkg"
        if (processedKeys.contains(key)) return
        processedKeys.add(key)

        Log.e("CashflowNotif", "Detected bank notification: [$pkg] $title: $fullText")

        try {
            val dir = applicationContext.filesDir
            val dataDir = File(dir, "data")
            if (!dataDir.exists()) dataDir.mkdirs()
            val extDir = applicationContext.getExternalFilesDir(null)

            val json = JSONObject()
            json.put("package", pkg)
            json.put("title", title)
            json.put("text", fullText)
            json.put("time", sbn.postTime)
            json.put("id", sbn.id)

            val line = json.toString() + "\n"

            // Write to filesDir
            FileWriter(File(dir, "incoming_notifications.jsonl"), true).use { it.append(line) }
            // Write to dataDir
            FileWriter(File(dataDir, "incoming_notifications.jsonl"), true).use { it.append(line) }
            // Write to external files dir (accessible from adb without root)
            if (extDir != null) {
                FileWriter(File(extDir, "incoming_notifications.jsonl"), true).use { it.append(line) }
            }

            Log.e("CashflowNotif", "Successfully queued bank notification to all targets")
        } catch (e: Exception) {
            Log.e("CashflowNotif", "Error saving notification", e)
        }
    }
}
