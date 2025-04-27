import SwiftUI

struct Achievement: Identifiable, Codable {
    let id: String
    let name: String
    let description: String
    let points: Int
    var isUnlocked: Bool
    let iconName: String
    let unlockedDate: Date?
    
    static let all: [Achievement] = [
        Achievement(
            id: "first_scan",
            name: NSLocalizedString("first_scan", comment: ""),
            description: NSLocalizedString("first_scan_desc", comment: ""),
            points: 10,
            isUnlocked: false,
            iconName: "checkmark.circle",
            unlockedDate: nil
        ),
        Achievement(
            id: "power_user",
            name: NSLocalizedString("power_user", comment: ""),
            description: NSLocalizedString("power_user_desc", comment: ""),
            points: 50,
            isUnlocked: false,
            iconName: "bolt.circle",
            unlockedDate: nil
        ),
        Achievement(
            id: "wireless_expert",
            name: NSLocalizedString("wireless_expert", comment: ""),
            description: NSLocalizedString("wireless_expert_desc", comment: ""),
            points: 100,
            isUnlocked: false,
            iconName: "wifi.circle",
            unlockedDate: nil
        ),
        Achievement(
            id: "ai_master",
            name: NSLocalizedString("ai_master", comment: ""),
            description: NSLocalizedString("ai_master_desc", comment: ""),
            points: 100,
            isUnlocked: false,
            iconName: "brain",
            unlockedDate: nil
        ),
        Achievement(
            id: "ar_explorer",
            name: NSLocalizedString("ar_explorer", comment: ""),
            description: NSLocalizedString("ar_explorer_desc", comment: ""),
            points: 75,
            isUnlocked: false,
            iconName: "arkit",
            unlockedDate: nil
        )
    ]
}

class AchievementManager: ObservableObject {
    static let shared = AchievementManager()
    
    @Published private(set) var achievements: [Achievement]
    @Published private(set) var totalPoints: Int = 0
    
    private let securityManager = SecurityManager.shared
    private let achievementsKey = "user_achievements"
    
    private init() {
        if let data = try? securityManager.loadFromKeychain(key: achievementsKey),
           let decoded = try? JSONDecoder().decode([Achievement].self, from: data) {
            achievements = decoded
        } else {
            achievements = Achievement.all
        }
        calculateTotalPoints()
    }
    
    func unlockAchievement(id: String) {
        guard let index = achievements.firstIndex(where: { $0.id == id }),
              !achievements[index].isUnlocked else { return }
        
        achievements[index].isUnlocked = true
        achievements[index].unlockedDate = Date()
        
        calculateTotalPoints()
        saveAchievements()
        
        // Post notification for UI update
        NotificationCenter.default.post(
            name: .achievementUnlocked,
            object: achievements[index]
        )
    }
    
    private func calculateTotalPoints() {
        totalPoints = achievements
            .filter { $0.isUnlocked }
            .reduce(0) { $0 + $1.points }
    }
    
    private func saveAchievements() {
        if let encoded = try? JSONEncoder().encode(achievements) {
            try? securityManager.saveToKeychain(key: achievementsKey, data: encoded)
        }
    }
}

extension Notification.Name {
    static let achievementUnlocked = Notification.Name("achievementUnlocked")
}

struct GamificationView: View {
    @StateObject private var achievementManager = AchievementManager.shared
    @State private var showUnlockAnimation = false
    @State private var lastUnlockedAchievement: Achievement?
    
    var body: some View {
        List {
            totalPointsSection
            achievementsSection
        }
        .navigationTitle("Achievements")
        .onReceive(NotificationCenter.default.publisher(for: .achievementUnlocked)) { notification in
            if let achievement = notification.object as? Achievement {
                lastUnlockedAchievement = achievement
                withAnimation {
                    showUnlockAnimation = true
                }
            }
        }
        .overlay(
            achievementUnlockOverlay
        )
    }
    
    private var totalPointsSection: some View {
        Section {
            HStack {
                Image(systemName: "star.circle.fill")
                    .foregroundColor(.yellow)
                Text("Total Points")
                Spacer()
                Text("\(achievementManager.totalPoints)")
                    .bold()
            }
        }
    }
    
    private var achievementsSection: some View {
        Section {
            ForEach(achievementManager.achievements) { achievement in
                AchievementRow(achievement: achievement)
            }
        }
    }
    
    private var achievementUnlockOverlay: some View {
        Group {
            if showUnlockAnimation,
               let achievement = lastUnlockedAchievement {
                ZStack {
                    Color.black.opacity(0.8)
                    
                    VStack(spacing: 16) {
                        Image(systemName: achievement.iconName)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 60, height: 60)
                            .foregroundColor(.yellow)
                        
                        Text("Achievement Unlocked!")
                            .font(.title2)
                            .bold()
                            .foregroundColor(.white)
                        
                        Text(achievement.name)
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Text("+\(achievement.points) points")
                            .foregroundColor(.yellow)
                    }
                    .padding()
                    .background(Color(UIColor.systemBackground).opacity(0.2))
                    .cornerRadius(20)
                }
                .transition(.opacity)
                .onAppear {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        withAnimation {
                            showUnlockAnimation = false
                        }
                    }
                }
            }
        }
    }
}

struct AchievementRow: View {
    let achievement: Achievement
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: achievement.iconName)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 30, height: 30)
                .foregroundColor(achievement.isUnlocked ? .yellow : .gray)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(achievement.name)
                    .font(.headline)
                
                Text(achievement.description)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                if let date = achievement.unlockedDate {
                    Text("Unlocked \(date.formatted(date: .abbreviated, time: .shortened))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            if achievement.isUnlocked {
                Text("+\(achievement.points)")
                    .bold()
                    .foregroundColor(.yellow)
            }
        }
        .padding(.vertical, 8)
        .opacity(achievement.isUnlocked ? 1 : 0.6)
    }
}

struct GamificationView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            GamificationView()
        }
    }
}
