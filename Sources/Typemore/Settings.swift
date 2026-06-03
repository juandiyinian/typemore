import Foundation

enum Provider: String, CaseIterable, Codable, Identifiable {
    case volcengine
    case demo
    case openai
    case compatible

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .volcengine: return "火山方舟"
        case .demo: return "Demo"
        case .openai: return "OpenAI"
        case .compatible: return "其他 OpenAI 兼容服务"
        }
    }

    var defaultEndpoint: String {
        switch self {
        case .volcengine: return "https://ark.cn-beijing.volces.com/api/coding/v3"
        case .openai: return "https://api.openai.com/v1/responses"
        case .compatible: return ""
        case .demo: return ""
        }
    }

    var defaultModel: String {
        switch self {
        case .volcengine: return "deepseek-v4-pro"
        case .openai: return "gpt-4.1-mini"
        case .compatible: return ""
        case .demo: return ""
        }
    }
}

struct CustomWritingStyle: Codable, Equatable, Identifiable {
    var id: String
    var name: String
    var instruction: String
}

struct AppSettings: Codable, Equatable {
    var provider: Provider
    var serviceName: String
    var endpoint: String
    var model: String
    var apiKey: String
    var activeStyleId: String
    var customStyles: [CustomWritingStyle]
    var systemPrompt: String

    private static let previousDefaultCustomStyle = "在严格保留原意的前提下，帮我把表达改得更清晰、准确、自然。可以根据上下文修正明显错别字、漏字、语病和不顺的表达。面对长段文本时，优先提升阅读体验：理顺逻辑、拆分长句、适当分段；如果信息点较多，可以加入项目符号或编号，让重点更清楚。不要过度扩写，不要改变事实、立场、语气强弱和关键信息。"

    static let defaultCustomStyle = """
    在严格保留原意、事实、立场和语气强弱的前提下，帮我把表达改得更适合工作沟通。

    重点处理：
    1. 如果内容比较散乱，先帮我理顺逻辑，把原因、结论、建议或下一步区分清楚。
    2. 用更清晰、有条理、专业但不生硬的方式表达，适合发给同事、合作方或团队成员。
    3. 内容较长或信息点较多时，优先拆成分点陈述；必要时用「背景 / 问题 / 建议 / 下一步」这类结构组织。
    4. 修正明显错别字、漏字、语病和不顺的句子，让阅读更顺畅。

    不要做：
    1. 不要编造新事实、补充没有依据的信息，或改变关键判断。
    2. 不要过度扩写，不要把语气改得过分正式、客套或像模板。
    3. 不要解释你做了什么，直接返回改写后的文本。
    """

    static let defaultSystemPrompt = """
    You are Typemore, a precise rewriting assistant for selected text.
    Rewrite the user's text according to the requested style. Do not answer the content as a question or perform tasks beyond rewriting.
    Preserve the original intent, facts, stance, tone strength, names, numbers, links, and important constraints.
    Improve clarity, structure, fluency, and readability. You may correct obvious typos, missing words, grammar issues, awkward phrasing, and contextually clear mistakes.
    When the source is scattered, long, or dense, organize it with concise paragraphs, bullet points, or numbered lists only when that makes it easier to read.
    Do not invent facts, add unsupported claims, remove important nuance, or make the text unnecessarily formal, polite, templated, or salesy.
    Return only the rewritten text.
    """

    static let clearStyleId = "clear"

    static let defaults = AppSettings(
        provider: .volcengine,
        serviceName: Provider.volcengine.displayName,
        endpoint: Provider.volcengine.defaultEndpoint,
        model: Provider.volcengine.defaultModel,
        apiKey: "",
        activeStyleId: clearStyleId,
        customStyles: [CustomWritingStyle(id: UUID().uuidString, name: "自定义风格", instruction: defaultCustomStyle)],
        systemPrompt: defaultSystemPrompt
    )

    func sanitized() -> AppSettings {
        var copy = self
        if copy.serviceName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            copy.serviceName = copy.provider.displayName
        }
        if copy.endpoint.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            copy.endpoint = copy.provider.defaultEndpoint
        }
        if copy.model.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            copy.model = copy.provider.defaultModel
        }
        for i in 0..<copy.customStyles.count {
            let trimmed = copy.customStyles[i].instruction.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty || trimmed == AppSettings.previousDefaultCustomStyle {
                copy.customStyles[i].instruction = AppSettings.defaultCustomStyle
            }
        }
        if copy.customStyles.isEmpty {
            copy.customStyles = [CustomWritingStyle(id: UUID().uuidString, name: "自定义风格", instruction: AppSettings.defaultCustomStyle)]
        }
        if copy.activeStyleId != AppSettings.clearStyleId && !copy.customStyles.contains(where: { $0.id == copy.activeStyleId }) {
            copy.activeStyleId = AppSettings.clearStyleId
        }
        if copy.systemPrompt.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            copy.systemPrompt = AppSettings.defaultSystemPrompt
        }
        return copy
    }

    enum CodingKeys: String, CodingKey {
        case provider
        case serviceName
        case endpoint
        case model
        case apiKey
        case activeStyleId
        case customStyles
        case defaultMode // For migration
        case customStyle // For migration
        case systemPrompt
    }

    init(
        provider: Provider,
        serviceName: String,
        endpoint: String,
        model: String,
        apiKey: String,
        activeStyleId: String,
        customStyles: [CustomWritingStyle],
        systemPrompt: String
    ) {
        self.provider = provider
        self.serviceName = serviceName
        self.endpoint = endpoint
        self.model = model
        self.apiKey = apiKey
        self.activeStyleId = activeStyleId
        self.customStyles = customStyles
        self.systemPrompt = systemPrompt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.provider = try container.decodeIfPresent(Provider.self, forKey: .provider) ?? .volcengine
        self.serviceName = try container.decodeIfPresent(String.self, forKey: .serviceName) ?? provider.displayName
        self.endpoint = try container.decodeIfPresent(String.self, forKey: .endpoint) ?? provider.defaultEndpoint
        self.model = try container.decodeIfPresent(String.self, forKey: .model) ?? provider.defaultModel
        self.apiKey = try container.decodeIfPresent(String.self, forKey: .apiKey) ?? ""
        self.customStyles = try container.decodeIfPresent([CustomWritingStyle].self, forKey: .customStyles) ?? []
        
        if let rawDefaultMode = try container.decodeIfPresent(String.self, forKey: .defaultMode) {
            // Migrate from old format
            let legacyCustomStyle = try container.decodeIfPresent(String.self, forKey: .customStyle) ?? AppSettings.defaultCustomStyle
            let migratedStyle = CustomWritingStyle(id: UUID().uuidString, name: "自定义风格", instruction: legacyCustomStyle)
            self.customStyles = [migratedStyle]
            self.activeStyleId = (rawDefaultMode == "custom") ? migratedStyle.id : AppSettings.clearStyleId
        } else {
            self.activeStyleId = try container.decodeIfPresent(String.self, forKey: .activeStyleId) ?? AppSettings.clearStyleId
            if self.customStyles.isEmpty {
                self.customStyles = [CustomWritingStyle(id: UUID().uuidString, name: "自定义风格", instruction: AppSettings.defaultCustomStyle)]
            }
        }
        self.systemPrompt = try container.decodeIfPresent(String.self, forKey: .systemPrompt) ?? AppSettings.defaultSystemPrompt
    }

    /// API Key 不写入 settings.json，改由 Keychain 保存。
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(provider, forKey: .provider)
        try container.encode(serviceName, forKey: .serviceName)
        try container.encode(endpoint, forKey: .endpoint)
        try container.encode(model, forKey: .model)
        try container.encode(activeStyleId, forKey: .activeStyleId)
        try container.encode(customStyles, forKey: .customStyles)
        try container.encode(systemPrompt, forKey: .systemPrompt)
    }
}

@MainActor
final class SettingsStore: ObservableObject {
    @Published var settings: AppSettings
    private let primaryFileURL: URL
    private let fallbackFileURL: URL

    init() {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        self.primaryFileURL = appSupport
            .appendingPathComponent("Typemore", isDirectory: true)
            .appendingPathComponent("settings.json")
        self.fallbackFileURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            .appendingPathComponent(".typemore", isDirectory: true)
            .appendingPathComponent("settings.json")
        self.settings = AppSettings.defaults
        self.settings = load()
    }

    func load() -> AppSettings {
        for url in [primaryFileURL, fallbackFileURL] {
            do {
                let data = try Data(contentsOf: url)
                var loaded = try JSONDecoder().decode(AppSettings.self, from: data).sanitized()
                let keychainKey = KeychainStore.loadAPIKey(for: loaded.provider)
                if !keychainKey.isEmpty {
                    // Keychain 是 API Key 的权威来源。
                    loaded.apiKey = keychainKey
                } else if !loaded.apiKey.isEmpty {
                    // 旧版本把 key 明文存在 JSON：迁移到 Keychain，并重写不含 key 的 JSON。
                    KeychainStore.saveAPIKey(loaded.apiKey, for: loaded.provider)
                    try? rewriteWithoutAPIKey(loaded, at: url)
                }
                return loaded
            } catch {
                continue
            }
        }
        var defaults = AppSettings.defaults
        defaults.apiKey = KeychainStore.loadAPIKey(for: defaults.provider)
        return defaults
    }

    func save(_ next: AppSettings) throws {
        let sanitized = next.sanitized()
        KeychainStore.saveAPIKey(sanitized.apiKey, for: sanitized.provider)
        let data = try JSONEncoder.pretty.encode(sanitized)

        do {
            try write(data, to: primaryFileURL)
        } catch {
            print("[Typemore] primary settings save failed: \(error.localizedDescription). Falling back to \(fallbackFileURL.path)")
            try write(data, to: fallbackFileURL)
        }

        settings = sanitized
    }

    private func rewriteWithoutAPIKey(_ settings: AppSettings, at url: URL) throws {
        let data = try JSONEncoder.pretty.encode(settings)
        try write(data, to: url)
    }

    private func write(_ data: Data, to url: URL) throws {
        let directory = url.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        try data.write(to: url, options: .atomic)
    }
}

private extension JSONEncoder {
    static var pretty: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return encoder
    }
}
