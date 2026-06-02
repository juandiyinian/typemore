# Typemore Product Notes

## Product promise

Typemore helps people turn rough typed thoughts into the expression they intended, without leaving the input flow they are already in.

## Interaction model

1. User selects rough text, or places the cursor near the text they want to improve.
2. User double-taps the right Option key.
3. Typemore captures the selected text or the current cursor-nearby target, adds surrounding context for understanding, rewrites it with the configured model service, and pastes only the replacement text back.
4. A tiny capsule shows progress, completion, and a short undo affordance.

## Product constraints

- The trigger UI should stay minimal and not expose style choices.
- Writing style belongs in settings.
- The default flow should feel ambient, keyboard-first, and close to system behavior.
- The app should keep working when caret bounds are unavailable by falling back to a stable position.
