import SwiftUI

struct AnalyticsDashboardView: View {
    @State private var openPorts: Int = 0
    @State private var closedPorts: Int = 0

    var body: some View {
        VStack {
            Text("Analytics Dashboard")
                .font(.largeTitle)
                .padding()

            HStack {
                VStack {
                    Text("Open Ports")
                        .font(.headline)
                    Text("\(openPorts)")
                        .font(.title)
                        .foregroundColor(.green)
                }
                .padding()

                VStack {
                    Text("Closed Ports")
                        .font(.headline)
                    Text("\(closedPorts)")
                        .font(.title)
                        .foregroundColor(.red)
                }
                .padding()
            }

            Spacer()
        }
        .onAppear {
            // Fetch analytics data here
            openPorts = 5
            closedPorts = 95
        }
    }
}

struct AnalyticsDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsDashboardView()
    }
}
