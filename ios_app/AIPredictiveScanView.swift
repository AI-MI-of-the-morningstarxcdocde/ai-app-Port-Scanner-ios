import SwiftUI
import Combine

struct AIPredictiveScanView: View {
    @StateObject private var coordinator = AppCoordinator.shared
    @State private var targetIP: String = ""
    @State private var scanResults: [String] = []
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""
    
    private var networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("AI Predictive Scan")
                .font(.title)
                .bold()
                .padding(.top)
            
            TextField("Target IP or Hostname", text: $targetIP)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .keyboardType(.numbersAndPunctuation)
            
            Button(action: startAIPredictiveScan) {
                HStack {
                    if coordinator.currentScanInProgress {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    }
                    Text(coordinator.currentScanInProgress ? "Scanning..." : "Start AI Scan")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(coordinator.currentScanInProgress ? Color.gray : Color.green)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .disabled(coordinator.currentScanInProgress || targetIP.isEmpty || !coordinator.hasUnlockedFeatures)
            .padding(.horizontal)
            
            if !coordinator.hasUnlockedFeatures {
                VStack(spacing: 8) {
                    Text("🔒 Premium Feature")
                        .font(.headline)
                    Text("Unlock AI predictive scanning by upgrading to Premium")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(10)
                .padding(.horizontal)
            }
            
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 8) {
                    ForEach(scanResults, id: \.self) { result in
                        Text(result)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color(UIColor.secondarySystemBackground))
                            .cornerRadius(8)
                    }
                }
                .padding(.horizontal)
            }
            
            Spacer()
        }
        .navigationTitle("AI Predictive Scan")
        .alert(isPresented: $showAlert) {
            Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
    }
    
    private func startAIPredictiveScan() {
        guard coordinator.startScan(target: targetIP, ports: "") else {
            alertMessage = "Please authenticate to start scanning"
            showAlert = true
            return
        }
        
        scanResults = ["Starting AI predictive scan on \(targetIP)..."]
        
        networkManager.performAIPredictiveScan(target: targetIP)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    coordinator.endScan()
                    switch completion {
                    case .failure(let error):
                        alertMessage = error.localizedDescription
                        showAlert = true
                    case .finished:
                        NotificationCenter.default.post(
                            name: .aiScanCompleted,
                            object: nil
                        )
                    }
                },
                receiveValue: { result in
                    scanResults = [
                        "AI Predictive Scan Results for \(targetIP):",
                        "Predicted open ports: \(result.predicted_open_ports.map(String.init).joined(separator: ", "))"
                    ]
                }
            )
            .store(in: &cancellables)
    }
}

struct AIPredictiveScanView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            AIPredictiveScanView()
        }
    }
}
