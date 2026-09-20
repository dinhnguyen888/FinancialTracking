package com.cashflowtracking.cashflowtracking

import android.content.ComponentName
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.service.notification.NotificationListenerService
import android.util.Log
import android.view.WindowManager
import androidx.core.view.WindowCompat
import io.flutter.embedding.android.FlutterFragmentActivity
import java.io.File

class MainActivity : FlutterFragmentActivity() {

    private val handler = Handler(Looper.getMainLooper())
    private var triggerWatcher: Runnable? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        configureWindowAppearance()
        startTriggerWatcher()
    }

    override fun onResume() {
        super.onResume()
        configureWindowAppearance()
        checkAndRebindNotificationListener()
    }

    override fun onDestroy() {
        super.onDestroy()
        triggerWatcher?.let { handler.removeCallbacks(it) }
    }

    private fun configureWindowAppearance() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                window.attributes.layoutInDisplayCutoutMode =
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }
            val darkBg = Color.parseColor("#0F172A")
            window.statusBarColor = darkBg
            window.navigationBarColor = darkBg

            val insetsController = WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = false
            insetsController.isAppearanceLightNavigationBars = false
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun checkAndRebindNotificationListener() {
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners") ?: ""
        val isGranted = flat.contains(packageName)
        
        try {
            val statusFile = File(filesDir, "permission_status.txt")
            statusFile.writeText(if (isGranted) "granted" else "denied")

            val dataDir = File(filesDir, "data")
            if (dataDir.exists()) {
                File(dataDir, "permission_status.txt").writeText(if (isGranted) "granted" else "denied")
            }
        } catch (e: Exception) {
            Log.e("CashflowNotif", "Error writing status file", e)
        }

        if (isGranted) {
            Log.i("CashflowNotif", "Permission is granted, forcing rebind of BankNotificationListener...")
            val componentName = ComponentName(this, BankNotificationListener::class.java)
            
            // 1. requestRebind on Android N (API 24+)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                try {
                    NotificationListenerService.requestRebind(componentName)
                    Log.i("CashflowNotif", "requestRebind requested successfully")
                } catch (e: Exception) {
                    Log.e("CashflowNotif", "requestRebind failed: ${e.message}")
                }
            }

            // 2. Component toggle trick: forces Android NotificationManagerService to reconnect listener
            try {
                val pm = packageManager
                pm.setComponentEnabledSetting(
                    componentName,
                    PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    PackageManager.DONT_KILL_APP
                )
                pm.setComponentEnabledSetting(
                    componentName,
                    PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                    PackageManager.DONT_KILL_APP
                )
                Log.i("CashflowNotif", "Component toggle completed successfully")
            } catch (e: Exception) {
                Log.e("CashflowNotif", "Component toggle failed: ${e.message}")
            }
        }
    }

    private fun startTriggerWatcher() {
        triggerWatcher = object : Runnable {
            override fun run() {
                try {
                    val trigger1 = File(filesDir, "request_settings.trigger")
                    val dataDir = File(filesDir, "data")
                    val trigger2 = File(dataDir, "request_settings.trigger")
                    val rebindTrigger1 = File(filesDir, "rebind.trigger")
                    val rebindTrigger2 = File(dataDir, "rebind.trigger")

                    if (trigger1.exists() || trigger2.exists()) {
                        trigger1.delete()
                        trigger2.delete()
                        Log.i("CashflowNotif", "Received request_settings trigger, opening settings...")
                        val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        startActivity(intent)
                    }

                    if (rebindTrigger1.exists() || rebindTrigger2.exists()) {
                        rebindTrigger1.delete()
                        rebindTrigger2.delete()
                        checkAndRebindNotificationListener()
                    }
                } catch (e: Exception) {
                    Log.e("CashflowNotif", "Error in trigger watcher", e)
                }
                handler.postDelayed(this, 1000)
            }
        }
        handler.post(triggerWatcher!!)
    }
}
