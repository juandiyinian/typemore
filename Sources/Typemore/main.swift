import AppKit

guard let instanceLock = InstanceLock.acquire() else {
    print("[Typemore] Another Typemore instance is already running. Exit.")
    exit(0)
}

let app = NSApplication.shared
let delegate = MainActor.assumeIsolated {
    let delegate = TypemoreApp()
    app.delegate = delegate
    return delegate
}
_ = instanceLock
app.run()
