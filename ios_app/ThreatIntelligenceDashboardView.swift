import SwiftUI

struct ThreatIntelligenceDashboardView: View {
    @State private var threatData: [String: String] = [
        "192.168.1.1": "No threats detected",
        "192.168.1.2": "Potential vulnerability: Open Telnet port",
        "192.168.1.3": "No threats detected"
    ]

    var body: some View {
        NavigationView {
            List(threatData.keys.sorted(), id: \ .self) { ip in
                VStack(alignment: .leading) {
                    Text("IP: \(ip)")
                        .font(.headline)
                    Text(threatData[ip] ?? "Unknown")
                        .font(.subheadline)
                        .foregroundColor(threatData[ip]?.contains("No threats") == true ? .green : .red)
                }
                .padding()
            }
            .navigationTitle("Threat Intelligence Dashboard")
        }
    }
}

struct ThreatIntelligenceDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        ThreatIntelligenceDashboardView()
    }
}