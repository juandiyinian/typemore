with open("Sources/Typemore/RewriteService.swift", "r") as f:
    content = f.read()

content = content.replace("            return demoRewrite(source, mode: settings.defaultMode)", "            return demoRewrite(source, settings: settings)")
content = content.replace("            output = demoRewrite(source, mode: settings.defaultMode)", "            output = demoRewrite(source, settings: settings)")
content = content.replace('perfLog("rewrite total: \\(Self.formatDuration(since: startedAt)), chars=\\(source.count), mode=\\(settings.defaultMode.rawValue)")', 'perfLog("rewrite total: \\(Self.formatDuration(since: startedAt)), chars=\\(source.count), style=\\(settings.activeStyleId)")')

build_instruction_old = """    private func buildInstruction(settings: AppSettings) -> String {
        if settings.defaultMode == .custom {
            return [
                RewriteMode.custom.instruction,
                "Custom writing style:",
                settings.customStyle
            ].joined(separator: "\\n")
        }
        return settings.defaultMode.instruction
    }"""
build_instruction_new = """    private func buildInstruction(settings: AppSettings) -> String {
        if settings.activeStyleId == AppSettings.clearStyleId {
            return \"\"\"
            Rewrite the text into a clear, natural, and well-structured version that works for everyday writing and workplace communication.

            Priorities:
            1. Preserve the original meaning, facts, stance, tone strength, names, numbers, links, and key details.
            2. If the source is scattered, reorganize it so the main point, context, reasoning, feedback, request, or next step is easier to follow.
            3. Make the wording concise but not thin; keep necessary nuance and make the expression more complete when the original is too rough.
            4. For longer or information-dense text, use short paragraphs, bullet points, or numbered lists when that improves readability.
            5. Correct obvious typos, missing words, grammar issues, and awkward phrasing.

            Avoid:
            1. Do not invent facts, add unsupported claims, or change the user's judgment.
            2. Do not make the text overly formal, overly polite, templated, or salesy.
            3. Do not explain the rewrite. Return only the rewritten text.
            \"\"\"
        } else if let style = settings.customStyles.first(where: { $0.id == settings.activeStyleId }) {
            return [
                "Rewrite it in the user's custom writing style.",
                "Custom writing style:",
                style.instruction
            ].joined(separator: "\\n")
        } else {
            return "Rewrite the text to be clear and concise."
        }
    }"""
content = content.replace(build_instruction_old, build_instruction_new)

demo_old = """    private func demoRewrite(_ text: String, mode: RewriteMode) -> String {
        let cleaned = text.replacingOccurrences(of: #"[ \\t]+"#, with: " ", options: .regularExpression)
            .replacingOccurrences(of: #"\\n{3,}"#, with: "\\n\\n", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        switch mode {
        case .custom:
            return "按我的文风改写：\\(ensureSentenceEnd(cleaned))"
        case .clear:
            return ensureSentenceEnd(cleaned)
        }
    }"""
demo_new = """    private func demoRewrite(_ text: String, settings: AppSettings) -> String {
        let cleaned = text.replacingOccurrences(of: #"[ \\t]+"#, with: " ", options: .regularExpression)
            .replacingOccurrences(of: #"\\n{3,}"#, with: "\\n\\n", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if settings.activeStyleId == AppSettings.clearStyleId {
            return ensureSentenceEnd(cleaned)
        } else {
            let name = settings.customStyles.first(where: { $0.id == settings.activeStyleId })?.name ?? "自定义"
            return "按\\(name)改写：\\(ensureSentenceEnd(cleaned))"
        }
    }"""
content = content.replace(demo_old, demo_new)

with open("Sources/Typemore/RewriteService.swift", "w") as f:
    f.write(content)
