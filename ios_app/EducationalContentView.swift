import SwiftUI

struct EducationalContentView: View {
    let topics = [
        "What is Port Scanning?",
        "Common Network Vulnerabilities",
        "How to Secure Your Network",
        "Understanding Firewalls",
        "Basics of Wireless Security"
    ]

    var body: some View {
        NavigationView {
            List(topics, id: \ .self) { topic in
                NavigationLink(destination: Text("Details about \(topic)")) {
                    Text(topic)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
            }
            .navigationTitle("Learn About Network Security")
        }
    }
}

struct EducationalContentView_Previews: PreviewProvider {
    static var previews: some View {
        EducationalContentView()
    }
}