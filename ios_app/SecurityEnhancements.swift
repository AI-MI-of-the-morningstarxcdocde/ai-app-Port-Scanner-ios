import Foundation
import LocalAuthentication
import CryptoKit
import Security

enum SecurityError: LocalizedError {
    case authenticationFailed
    case biometricsNotAvailable
    case keychainError
    case encryptionError
    case invalidData
    
    var errorDescription: String? {
        switch self {
        case .authenticationFailed:
            return NSLocalizedString("auth_failed", comment: "")
        case .biometricsNotAvailable:
            return NSLocalizedString("biometrics_unavailable", comment: "")
        case .keychainError:
            return NSLocalizedString("keychain_error", comment: "")
        case .encryptionError:
            return NSLocalizedString("encryption_error", comment: "")
        case .invalidData:
            return NSLocalizedString("invalid_data", comment: "")
        }
    }
}

class SecurityManager {
    static let shared = SecurityManager()
    private let context = LAContext()
    private let keychainService = "com.morningstar.advancedportscanner"
    private var encryptionKey: SymmetricKey?
    
    private init() {
        generateEncryptionKey()
    }
    
    // MARK: - Authentication
    
    func authenticateUser() async throws -> Bool {
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil) else {
            throw SecurityError.biometricsNotAvailable
        }
        
        return try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: NSLocalizedString("auth_scan_message", comment: "")
        )
    }
    
    // MARK: - Secure Storage
    
    func saveToKeychain(key: String, data: Data) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status == errSecDuplicateItem {
            let updateQuery: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrService as String: keychainService,
                kSecAttrAccount as String: key
            ]
            
            let attributes: [String: Any] = [
                kSecValueData as String: data
            ]
            
            let updateStatus = SecItemUpdate(
                updateQuery as CFDictionary,
                attributes as CFDictionary
            )
            
            guard updateStatus == errSecSuccess else {
                throw SecurityError.keychainError
            }
        } else if status != errSecSuccess {
            throw SecurityError.keychainError
        }
    }
    
    func loadFromKeychain(key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data else {
            throw SecurityError.keychainError
        }
        
        return data
    }
    
    func removeFromKeychain(key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw SecurityError.keychainError
        }
    }
    
    // MARK: - Encryption
    
    private func generateEncryptionKey() {
        if let keyData = try? loadFromKeychain(key: "encryption_key") {
            encryptionKey = SymmetricKey(data: keyData)
        } else {
            encryptionKey = SymmetricKey(size: .bits256)
            if let key = encryptionKey {
                try? saveToKeychain(key: "encryption_key", data: key.withUnsafeBytes { Data($0) })
            }
        }
    }
    
    func encrypt(_ data: Data) throws -> Data {
        guard let key = encryptionKey else {
            throw SecurityError.encryptionError
        }
        
        let sealedBox = try AES.GCM.seal(data, using: key)
        return sealedBox.combined ?? Data()
    }
    
    func decrypt(_ data: Data) throws -> Data {
        guard let key = encryptionKey else {
            throw SecurityError.encryptionError
        }
        
        let sealedBox = try AES.GCM.SealedBox(combined: data)
        return try AES.GCM.open(sealedBox, using: key)
    }
    
    // MARK: - Request Security
    
    func secureRequest(_ request: URLRequest) -> URLRequest {
        var secureRequest = request
        
        // Add security headers
        secureRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        secureRequest.setValue(generateNonce(), forHTTPHeaderField: "X-Nonce")
        secureRequest.setValue(String(Date().timeIntervalSince1970), forHTTPHeaderField: "X-Timestamp")
        
        // Add request signature
        if let url = request.url?.absoluteString,
           let method = request.httpMethod {
            let signature = generateRequestSignature(url: url, method: method, timestamp: Date())
            secureRequest.setValue(signature, forHTTPHeaderField: "X-Signature")
        }
        
        return secureRequest
    }
    
    private func getAuthToken() -> String {
        if let tokenData = try? loadFromKeychain(key: "auth_token"),
           let token = String(data: tokenData, encoding: .utf8) {
            return token
        }
        return ""
    }
    
    private func generateNonce() -> String {
        let nonce = UUID().uuidString
        return nonce
    }
    
    private func generateRequestSignature(url: String, method: String, timestamp: Date) -> String {
        let dataToSign = "\(method):\(url):\(timestamp.timeIntervalSince1970)"
        if let data = dataToSign.data(using: .utf8) {
            let signature = HMAC<SHA256>.authenticationCode(
                for: data,
                using: encryptionKey ?? SymmetricKey(size: .bits256)
            )
            return Data(signature).base64EncodedString()
        }
        return ""
    }
    
    // MARK: - Certificate Pinning
    
    func validateServerCertificate(_ serverTrust: SecTrust, domain: String) -> Bool {
        let policies = [SecPolicyCreateSSL(true, domain as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFArray)
        
        var error: CFError?
        if #available(iOS 13.0, *) {
            guard SecTrustEvaluateWithError(serverTrust, &error) else {
                return false
            }
        } else {
            var result: SecTrustResultType = .invalid
            guard SecTrustEvaluate(serverTrust, &result) == errSecSuccess else {
                return false
            }
            guard result == .proceed || result == .unspecified else {
                return false
            }
        }
        
        // Get the server's public key
        guard let serverKey = SecTrustCopyPublicKey(serverTrust) else {
            return false
        }
        
        // Compare with pinned certificate
        if let pinnedCertData = loadPinnedCertificate(),
           let pinnedCert = SecCertificateCreateWithData(nil, pinnedCertData as CFData),
           let pinnedKey = SecCertificateCopyPublicKey(pinnedCert) {
            return serverKey == pinnedKey
        }
        
        return false
    }
    
    private func loadPinnedCertificate() -> Data? {
        // Load the pinned certificate from the bundle
        if let certPath = Bundle.main.path(forResource: "server-cert", ofType: "der"),
           let certData = try? Data(contentsOf: URL(fileURLWithPath: certPath)) {
            return certData
        }
        return nil
    }
}
