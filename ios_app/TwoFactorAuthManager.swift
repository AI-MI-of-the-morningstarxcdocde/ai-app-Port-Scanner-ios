import Foundation
import LocalAuthentication

class TwoFactorAuthManager: ObservableObject {
    @Published var isAuthenticated: Bool = false
    private let context = LAContext()
    private var error: NSError?
    
    var canUseBiometrics: Bool {
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
    
    func authenticateUser(completion: @escaping (Bool) -> Void) {
        let reason = "Authenticate to access the app"
        
        if canUseBiometrics {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
                DispatchQueue.main.async {
                    if success {
                        self.isAuthenticated = true
                        completion(true)
                    } else {
                        // Fallback to PIN code
                        self.authenticateWithPIN(completion: completion)
                    }
                }
            }
        } else {
            // Biometrics not available, use PIN
            authenticateWithPIN(completion: completion)
        }
    }
    
    private func authenticateWithPIN(completion: @escaping (Bool) -> Void) {
        // In a real app, implement a secure PIN verification
        // For demo purposes, assume PIN is correct
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.isAuthenticated = true
            completion(true)
        }
    }
    
    func generateTOTP() -> String {
        // Generate a Time-based One-Time Password
        // In a real app, implement TOTP algorithm (RFC 6238)
        let digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return (0..<6).map { _ in digits.randomElement()! }.joined()
    }
}