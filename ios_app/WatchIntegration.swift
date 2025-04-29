import SwiftUI
import WatchConnectivity

class WatchIntegration: NSObject, ObservableObject, WCSessionDelegate {
    @Published var message: String = ""

    override init() {
        super.init()
        if WCSession.isSupported() {
            let session = WCSession.default
            session.delegate = self
            session.activate()
        }
    }

    func sendMessage(_ message: String) {
        if WCSession.default.isReachable {
            WCSession.default.sendMessage(["message": message], replyHandler: nil, errorHandler: nil)
        }
    }

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        // Handle activation
    }

    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        DispatchQueue.main.async {
            self.message = message["message"] as? String ?? ""
        }
    }
}