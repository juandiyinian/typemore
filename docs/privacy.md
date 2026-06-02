# Privacy

Typemore only processes text that you actively trigger for rewriting. This can be selected text, or the target text around the current cursor when no text is selected.

When you use a real model provider, the target text and necessary surrounding context are sent to the endpoint and model configured in Typemore settings. Typemore does not run its own backend, does not collect analytics, and does not upload your API key to this repository.

Typemore prefers the macOS Accessibility API to read and replace text. When an app is unreliable, Typemore temporarily uses the system clipboard to copy or paste, then restores the previous clipboard contents afterward. If you use a third-party clipboard manager, that manager may record the intermediate content. Avoid triggering Typemore in sensitive input fields.

Your API key and settings are stored locally in this Mac's Application Support directory.
