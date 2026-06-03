import re

with open("Sources/Typemore/Settings.swift", "r") as f:
    content = f.read()

# Remove RewriteMode
content = re.sub(r'enum RewriteMode: String, CaseIterable, Codable, Identifiable \{.*?\n\}\n\n', '', content, flags=re.DOTALL)

# Add CustomWritingStyle
custom_style_struct = """struct CustomWritingStyle: Codable, Equatable, Identifiable {
    var id: String
    var name: String
    var instruction: String
}

"""

content = content.replace("struct AppSettings: Codable, Equatable {\n", custom_style_struct + "struct AppSettings: Codable, Equatable {\n")

content = content.replace("    var defaultMode: RewriteMode\n    var customStyle: String\n", "    var activeStyleId: String\n    var customStyles: [CustomWritingStyle]\n")

content = content.replace("""    static let defaults = AppSettings(
        provider: .volcengine,
        serviceName: Provider.volcengine.displayName,
        endpoint: Provider.volcengine.defaultEndpoint,
        model: Provider.volcengine.defaultModel,
        apiKey: "",
        defaultMode: .clear,
        customStyle: defaultCustomStyle,
        systemPrompt: defaultSystemPrompt
    )""", """    static let clearStyleId = "clear"

    static let defaults = AppSettings(
        provider: .volcengine,
        serviceName: Provider.volcengine.displayName,
        endpoint: Provider.volcengine.defaultEndpoint,
        model: Provider.volcengine.defaultModel,
        apiKey: "",
        activeStyleId: clearStyleId,
        customStyles: [CustomWritingStyle(id: UUID().uuidString, name: "自定义风格", instruction: defaultCustomStyle)],
        systemPrompt: defaultSystemPrompt
    )""")

content = content.replace("""        let trimmedCustomStyle = copy.customStyle.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmedCustomStyle.isEmpty || trimmedCustomStyle == AppSettings.previousDefaultCustomStyle {
            copy.customStyle = AppSettings.defaultCustomStyle
        }""", """        for i in 0..<copy.customStyles.count {
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
        }""")

content = content.replace("""        case defaultMode
        case customStyle""", """        case activeStyleId
        case customStyles
        case defaultMode // For migration
        case customStyle // For migration""")

content = content.replace("""    init(
        provider: Provider,
        serviceName: String,
        endpoint: String,
        model: String,
        apiKey: String,
        defaultMode: RewriteMode,
        customStyle: String,
        systemPrompt: String
    ) {
        self.provider = provider
        self.serviceName = serviceName
        self.endpoint = endpoint
        self.model = model
        self.apiKey = apiKey
        self.defaultMode = defaultMode
        self.customStyle = customStyle
        self.systemPrompt = systemPrompt
    }""", """    init(
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
    }""")

init_from_decoder_old = """        if let rawDefaultMode = try container.decodeIfPresent(String.self, forKey: .defaultMode) {
            self.defaultMode = RewriteMode(rawValue: rawDefaultMode) ?? .clear
        } else {
            self.defaultMode = .clear
        }
        self.customStyle = try container.decodeIfPresent(String.self, forKey: .customStyle) ?? AppSettings.defaultCustomStyle"""

init_from_decoder_new = """        self.customStyles = try container.decodeIfPresent([CustomWritingStyle].self, forKey: .customStyles) ?? []
        
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
        }"""
content = content.replace(init_from_decoder_old, init_from_decoder_new)

encode_old = """        try container.encode(defaultMode, forKey: .defaultMode)
        try container.encode(customStyle, forKey: .customStyle)"""
encode_new = """        try container.encode(activeStyleId, forKey: .activeStyleId)
        try container.encode(customStyles, forKey: .customStyles)"""
content = content.replace(encode_old, encode_new)

with open("Sources/Typemore/Settings.swift", "w") as f:
    f.write(content)
