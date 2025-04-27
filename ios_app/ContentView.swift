import SwiftUI
import Combine

struct ContentView: View {
    @StateObject private var themeManager = ThemeManager()
    @StateObject private var coordinator = AppCoordinator.shared
    @State private var targetIP: String = ""
    @State private var portRange: String = "1-1000"
    @State private var scanResults: [String] = []
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""
    
    private var networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            TextField("Enter target IP", text: $targetIP)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .keyboardType(.numbersAndPunctuation)
            
            TextField("Enter port range (e.g. 1-1000)", text: $portRange)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .keyboardType(.numbersAndPunctuation)
            
            Button(action: startScan) {
                HStack {
                    if coordinator.currentScanInProgress {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    }
                    Text(coordinator.currentScanInProgress ? "Scanning..." : "Start Scan")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(coordinator.currentScanInProgress ? Color.gray : Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .disabled(coordinator.currentScanInProgress || targetIP.isEmpty)
            .padding(.horizontal)
            
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
        .navigationTitle("Port Scanner")
        .navigationBarItems(trailing: Button(action: {
            themeManager.toggleTheme()
        }) {
            Image(systemName: themeManager.isDarkMode ? "sun.max.fill" : "moon.fill")
        })
        .alert(isPresented: $showAlert) {
            Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
    }
    
    private func startScan() {
        guard coordinator.startScan(target: targetIP, ports: portRange) else {
            alertMessage = "Please authenticate to start scanning"
            showAlert = true
            return
        }
        
        scanResults = ["Starting scan on \(targetIP) ports \(portRange)..."]
        
        networkManager.performPortScan(target: targetIP, ports: portRange)
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
                            name: .scanCompleted,
                            object: ScanResult(target: targetIP, ports: portRange, results: scanResults)
                        )
                    }
                },
                receiveValue: { result in
                    scanResults = result.results
                }
            )
            .store(in: &cancellables)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            ContentView()
        }
    }
}
