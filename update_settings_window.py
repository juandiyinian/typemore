import re

with open("Sources/Typemore/SettingsWindow.swift", "r") as f:
    content = f.read()

# Remove @State private var selectedStyle
content = re.sub(r'    @State private var selectedStyle: StyleTab\n', '', content)
content = re.sub(r'        _selectedStyle = State\(initialValue: store\.settings\.defaultMode == \.custom \? \.custom : \.default\)\n', '', content)

# Update onReceive for settings
on_receive_old = """        .onReceive(store.$settings) { settings in
            selectedStyle = settings.defaultMode == .custom ? .custom : .default
        }"""
content = content.replace(on_receive_old, "")

# Replace writingCard
writing_card_old = """    private var writingCard: some View {
        SettingsCard(title: "Writing Style") {
            VStack(spacing: 14) {
                StyleTabSelector(selection: $selectedStyle)
                    .onChange(of: selectedStyle) { tab in
                        draft.defaultMode = tab == .custom ? .custom : .clear
                    }
                if selectedStyle == .custom {
                    SettingsEditor(
                        title: "自定义风格",
                        text: $draft.customStyle,
                        minHeight: 116,
                        placeholder: "描述你希望 Typemore 遵循的表达风格。"
                    )
                } else {
                    DefaultStylePreview()
                }
            }
        }
    }"""

writing_card_new = """    private var writingCard: some View {
        SettingsCard(title: "Writing Style") {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    Text("选择风格")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(SettingsTheme.secondaryText)
                    Spacer()
                    Button(action: addCustomStyle) {
                        Image(systemName: "plus")
                            .font(.system(size: 12, weight: .bold))
                    }
                    .buttonStyle(SecondarySettingsButtonStyle())
                }
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        SegmentButton(title: "默认风格", isSelected: draft.activeStyleId == AppSettings.clearStyleId) {
                            draft.activeStyleId = AppSettings.clearStyleId
                        }
                        ForEach(draft.customStyles) { style in
                            SegmentButton(title: style.name, isSelected: draft.activeStyleId == style.id) {
                                draft.activeStyleId = style.id
                            }
                        }
                    }
                }
                
                if draft.activeStyleId == AppSettings.clearStyleId {
                    DefaultStylePreview()
                } else if let index = draft.customStyles.firstIndex(where: { $0.id == draft.activeStyleId }) {
                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            SettingsField(title: "风格名称", text: Binding(
                                get: { self.draft.customStyles[index].name },
                                set: { self.draft.customStyles[index].name = $0 }
                            ), placeholder: "例如：正式邮件")
                            Spacer()
                            Button("删除") {
                                deleteCustomStyle(at: index)
                            }
                            .buttonStyle(SecondarySettingsButtonStyle())
                            .foregroundStyle(SettingsTheme.error)
                        }
                        SettingsEditor(
                            title: "风格指令",
                            text: Binding(
                                get: { self.draft.customStyles[index].instruction },
                                set: { self.draft.customStyles[index].instruction = $0 }
                            ),
                            minHeight: 116,
                            placeholder: "描述你希望 Typemore 遵循的表达风格。"
                        )
                    }
                }
            }
        }
    }

    private func addCustomStyle() {
        let newStyle = CustomWritingStyle(id: UUID().uuidString, name: "新风格", instruction: "")
        draft.customStyles.append(newStyle)
        draft.activeStyleId = newStyle.id
    }

    private func deleteCustomStyle(at index: Int) {
        draft.customStyles.remove(at: index)
        if draft.customStyles.isEmpty {
            draft.activeStyleId = AppSettings.clearStyleId
        } else {
            draft.activeStyleId = draft.customStyles.first!.id
        }
    }"""
content = content.replace(writing_card_old, writing_card_new)

# Update save
save_old = """            draft.serviceName = draft.provider.displayName
            draft.defaultMode = selectedStyle == .custom ? .custom : .clear
            if draft.serviceName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {"""
save_new = """            draft.serviceName = draft.provider.displayName
            if draft.serviceName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {"""
content = content.replace(save_old, save_new)

# Update reset
reset_old = """    private func reset() {
        draft = AppSettings.defaults
        selectedStyle = .default
        save()
    }"""
reset_new = """    private func reset() {
        draft = AppSettings.defaults
        save()
    }"""
content = content.replace(reset_old, reset_new)

# Remove StyleTab and StyleTabSelector
content = re.sub(r'private enum StyleTab: String, CaseIterable, Identifiable \{.*?\n\}\n\n', '', content, flags=re.DOTALL)
content = re.sub(r'private struct StyleTabSelector: View \{.*?\n\}\n\n', '', content, flags=re.DOTALL)

with open("Sources/Typemore/SettingsWindow.swift", "w") as f:
    f.write(content)
