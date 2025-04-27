import SwiftUI

enum ThemeColor: String, CaseIterable, Codable {
    case blue
    case green
    case purple
    case orange
    case red
    
    var color: Color {
        switch self {
        case .blue: return .blue
        case .green: return .green
        case .purple: return .purple
        case .orange: return .orange
        case .red: return .red
        }
    }
}

struct Theme: Codable {
    var isDarkMode: Bool
    var accentColor: ThemeColor
    var useSystemTheme: Bool
}

class ThemeManager: ObservableObject {
    @Published var theme: Theme {
        didSet {
            saveTheme()
        }
    }
    
    @Published var currentColorScheme: ColorScheme {
        didSet {
            if !theme.useSystemTheme {
                theme.isDarkMode = currentColorScheme == .dark
            }
        }
    }
    
    private let defaults = UserDefaults.standard
    private let themeKey = "com.morningstar.advancedportscanner.theme"
    
    init() {
        if let data = defaults.data(forKey: themeKey),
           let savedTheme = try? JSONDecoder().decode(Theme.self, from: data) {
            theme = savedTheme
        } else {
            theme = Theme(
                isDarkMode: false,
                accentColor: .blue,
                useSystemTheme: true
            )
        }
        
        currentColorScheme = theme.useSystemTheme ? .light : (theme.isDarkMode ? .dark : .light)
        
        if theme.useSystemTheme {
            NotificationCenter.default.addObserver(
                self,
                selector: #selector(systemThemeChanged),
                name: NSNotification.Name("systemThemeChanged"),
                object: nil
            )
        }
    }
    
    func toggleTheme() {
        if !theme.useSystemTheme {
            theme.isDarkMode.toggle()
            currentColorScheme = theme.isDarkMode ? .dark : .light
        }
    }
    
    func setAccentColor(_ color: ThemeColor) {
        theme.accentColor = color
    }
    
    func setUseSystemTheme(_ use: Bool) {
        theme.useSystemTheme = use
        if use {
            // Update to match system theme
            let systemTheme = UITraitCollection.current.userInterfaceStyle
            currentColorScheme = systemTheme == .dark ? .dark : .light
            theme.isDarkMode = systemTheme == .dark
        }
    }
    
    @objc private func systemThemeChanged() {
        if theme.useSystemTheme {
            let systemTheme = UITraitCollection.current.userInterfaceStyle
            currentColorScheme = systemTheme == .dark ? .dark : .light
            theme.isDarkMode = systemTheme == .dark
        }
    }
    
    private func saveTheme() {
        if let encoded = try? JSONEncoder().encode(theme) {
            defaults.set(encoded, forKey: themeKey)
        }
    }
}

struct ThemeSettingsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Form {
            Section(header: Text("Appearance")) {
                Toggle("Use System Theme", isOn: Binding(
                    get: { themeManager.theme.useSystemTheme },
                    set: { themeManager.setUseSystemTheme($0) }
                ))
                
                if !themeManager.theme.useSystemTheme {
                    Toggle("Dark Mode", isOn: Binding(
                        get: { themeManager.theme.isDarkMode },
                        set: { _ in themeManager.toggleTheme() }
                    ))
                }
            }
            
            Section(header: Text("Accent Color")) {
                ForEach(ThemeColor.allCases, id: \.self) { color in
                    HStack {
                        Circle()
                            .fill(color.color)
                            .frame(width: 20, height: 20)
                        
                        Text(color.rawValue.capitalized)
                        
                        Spacer()
                        
                        if themeManager.theme.accentColor == color {
                            Image(systemName: "checkmark")
                                .foregroundColor(.blue)
                        }
                    }
                    .contentShape(Rectangle())
                    .onTapGesture {
                        themeManager.setAccentColor(color)
                    }
                }
            }
        }
        .navigationTitle("Theme Settings")
    }
}
