package com.cashflowtracking.cashflowtracking

import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.WindowManager
import androidx.core.app.NotificationManagerCompat
import androidx.core.view.WindowCompat
import io.flutter.embedding.android.FlutterFragmentActivity
import java.io.File

class MainActivity : FlutterFragmentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        configureWindowAppearance()
        handleIntent(intent)
        checkAndUpdatePermissionFlag()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
        checkAndUpdatePermissionFlag()
    }

    override fun onResume() {
        super.onResume()
        configureWindowAppearance()
        checkAndUpdatePermissionFlag()
    }

    private fun configureWindowAppearance() {
        try {
            // 1. Prevent Android from letterboxing or adding a black bar across punch-hole / notch
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                window.attributes.layoutInDisplayCutoutMode =
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }

            // 2. Seamlessly blend status bar and navigation bar with app dark background
            val darkBg = Color.parseColor("#0F172A")
            window.statusBarColor = darkBg
            window.navigationBarColor = darkBg

            // 3. Ensure white/light status bar text & icons
            val insetsController = WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = false
            insetsController.isAppearanceLightNavigationBars = false
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun handleIntent(intent: Intent?) {
        val data = intent?.data ?: return
        if (data.scheme == "cashflow" && data.host == "settings") {
            try {
                val settingsIntent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                settingsIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                startActivity(settingsIntent)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun checkAndUpdatePermissionFlag() {
        try {
            val enabled = NotificationManagerCompat.getEnabledListenerPackages(this).contains(packageName)
            val dir = applicationContext.filesDir
            val dataDir = File(dir, "data")
            val extDir = applicationContext.getExternalFilesDir(null)

            val targets = mutableListOf(
                File(dir, "notification_permission_enabled.flag"),
                File(dataDir, "notification_permission_enabled.flag")
            )
            if (extDir != null) {
                targets.add(File(extDir, "notification_permission_enabled.flag"))
            }

            for (f in targets) {
                try {
                    if (enabled) {
                        if (!f.exists()) f.createNewFile()
                    } else {
                        if (f.exists()) f.delete()
                    }
                } catch (e: Exception) {}
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
