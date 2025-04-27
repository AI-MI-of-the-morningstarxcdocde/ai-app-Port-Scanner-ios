import SwiftUI
import Combine

struct WirelessAttackView: View {
    @StateObject private var coordinator = AppCoordinator.shared
    @State private var targetIP: String = ""
    @State private var attackLog: [String] = []
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""
    
    private var networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Wireless Attack")
                .font(.title)
                .bold()
                .padding(.top)
            
            TextField("Enter target IP", text: $targetIP)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .keyboardType(.numbersAndPunctuation)
            
            Button(action: startWirelessAttack) {
                HStack {
                    if coordinator.currentScanInProgress {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    }
                    Text(coordinator.currentScanInProgress ? "Attacking..." : "Start Wireless Attack")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(coordinator.currentScanInProgress ? Color.gray : Color.red)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .disabled(coordinator.currentScanInProgress || targetIP.isEmpty || !coordinator.hasUnlockedFeatures)
            .padding(.horizontal)
            
            if !coordinator.hasUnlockedFeatures {
                VStack(spacing: 8) {
                    Text("🔒 Premium Feature")
                        .font(.headline)
                    Text("Unlock wireless attack capabilities by upgrading to Premium")
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
                    ForEach(attackLog, id: \.self) { log in
                        Text(log)
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
        .navigationTitle("Wireless Attack")
        .alert(isPresented: $showAlert) {
            Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
    }
    
    private func startWirelessAttack() {
        guard coordinator.startScan(target: targetIP, ports: "") else {
            alertMessage = "Please authenticate to start wireless attack"
            showAlert = true
            return
        }
        
        attackLog = ["Starting wireless attack on \(targetIP)..."]
        
        networkManager.performWirelessAttack(target: targetIP)
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
                            name: .wirelessAttackCompleted,
                            object: nil
                        )
                    }
                },
                receiveValue: { result in
                    attackLog.append("Attack status: \(result.status)")
                }
            )
            .store(in: &cancellables)
    }
}

struct WirelessAttackView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            WirelessAttackView()
        }
    }
}
