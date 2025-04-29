import SwiftUI

class ThemeManager: ObservableObject {
    @Published var isDarkMode: Bool = false

    func toggleTheme() {
        isDarkMode.toggle()
    }
}
