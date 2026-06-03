import Foundation
import Security

/// API Key 存储在 macOS Keychain，而不是明文写入 settings.json。
enum KeychainStore {
    private static let service = "Typemore"
    private static let account = "default-api-key"

    static func loadAPIKey(for provider: Provider) -> String {
        let account = "api-key-\(provider.rawValue)"
        var query = baseQuery(account: account)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        if status == errSecSuccess,
           let data = result as? Data,
           let value = String(data: data, encoding: .utf8) {
            return value
        }
        
        // Fallback to old default key for backward compatibility
        var fallbackQuery = baseQuery(account: "default-api-key")
        fallbackQuery[kSecReturnData as String] = true
        fallbackQuery[kSecMatchLimit as String] = kSecMatchLimitOne
        
        var fallbackResult: CFTypeRef?
        let fallbackStatus = SecItemCopyMatching(fallbackQuery as CFDictionary, &fallbackResult)
        if fallbackStatus == errSecSuccess,
           let data = fallbackResult as? Data,
           let value = String(data: data, encoding: .utf8) {
            return value
        }
        
        return ""
    }

    @discardableResult
    static func saveAPIKey(_ value: String, for provider: Provider) -> Bool {
        let account = "api-key-\(provider.rawValue)"
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return deleteAPIKey(for: provider)
        }
        guard let data = trimmed.data(using: .utf8) else { return false }

        let query = baseQuery(account: account)
        let attributes: [String: Any] = [kSecValueData as String: data]

        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if updateStatus == errSecSuccess {
            return true
        }
        if updateStatus == errSecItemNotFound {
            var addQuery = query
            addQuery[kSecValueData as String] = data
            addQuery[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
            return SecItemAdd(addQuery as CFDictionary, nil) == errSecSuccess
        }
        return false
    }

    @discardableResult
    static func deleteAPIKey(for provider: Provider) -> Bool {
        let account = "api-key-\(provider.rawValue)"
        let status = SecItemDelete(baseQuery(account: account) as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }

    private static func baseQuery(account: String) -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
    }
}
