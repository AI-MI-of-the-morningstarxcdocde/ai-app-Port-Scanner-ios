import SwiftUI

struct GamificationView: View {
    @State private var achievements: [String] = ["First Scan Completed", "Found 10 Open Ports"]
    @State private var leaderboard: [String: Int] = ["User1": 150, "User2": 120, "User3": 100]

    var body: some View {
        NavigationView {
            VStack {
                List(achievements, id: \ .self) { achievement in
                    Text(achievement)
                        .padding()
                        .background(Color.green.opacity(0.2))
                        .cornerRadius(8)
                }
                .navigationTitle("Achievements")

                Text("Leaderboard")
                    .font(.headline)
                    .padding()

                List(leaderboard.sorted(by: { $0.value > $1.value }), id: \ .key) { user, score in
                    HStack {
                        Text(user)
                        Spacer()
                        Text("\(score) points")
                    }
                }
            }
        }
    }
}

struct GamificationView_Previews: PreviewProvider {
    static var previews: some View {
        GamificationView()
    }
}
