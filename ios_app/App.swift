import Intents

@main
struct AdvancedPortScannerApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    init() {
        requestSiriAuthorization()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }

    func requestSiriAuthorization() {
        INPreferences.requestSiriAuthorization { status in
            if status == .authorized {
                print("Siri Shortcuts authorized.")
            } else {
                print("Siri Shortcuts not authorized.")
            }
        }
    }

    func addSiriShortcut(for action: String) {
        let activity = NSUserActivity(activityType: "com.morningstar.portscanner.")
        activity.title = action
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        activity.persistentIdentifier = NSUserActivityPersistentIdentifier(action)
        activity.suggestedInvocationPhrase = "Start a port scan"
        UIApplication.shared.shortcutItems = [UIApplicationShortcutItem(type: action, localizedTitle: action)]
    }
}
