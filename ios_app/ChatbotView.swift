import SwiftUI
import Combine

struct Message: Identifiable {
    let id = UUID()
    let content: String
    let isUser: Bool
    let timestamp: Date
}

class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var inputMessage = ""
    @Published var isTyping = false
    
    private let featureCoordinator = FeatureCoordinator.shared
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        messages.append(Message(
            content: "Hello! I'm your security scanning assistant. I can help you interpret scan results and provide security recommendations. What would you like to know?",
            isUser: false,
            timestamp: Date()
        ))
        
        setupScanObservers()
    }
    
    private func setupScanObservers() {
        NotificationCenter.default.publisher(for: .scanCompleted)
            .sink { [weak self] notification in
                if let result = notification.object as? ScanResult {
                    self?.handleNewScanResult(result)
                }
            }
            .store(in: &cancellables)
    }
    
    func sendMessage() {
        guard !inputMessage.isEmpty else { return }
        
        let userMessage = Message(content: inputMessage, isUser: true, timestamp: Date())
        messages.append(userMessage)
        
        let query = inputMessage
        inputMessage = ""
        
        processUserQuery(query)
    }
    
    private func processUserQuery(_ query: String) {
        isTyping = true
        
        // Simulate AI processing time
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            guard let self = self else { return }
            
            let response = self.generateResponse(for: query)
            let botMessage = Message(content: response, isUser: false, timestamp: Date())
            self.messages.append(botMessage)
            self.isTyping = false
        }
    }
    
    private func generateResponse(for query: String) -> String {
        let lowercaseQuery = query.lowercased()
        
        if lowercaseQuery.contains("port") && lowercaseQuery.contains("scan") {
            return "To start a port scan, enter your target IP address and port range in the main scanner view. I can help you interpret the results once the scan is complete."
        } else if lowercaseQuery.contains("vulnerab") {
            return "I can help you identify vulnerabilities in your target systems. Would you like me to explain the different types of vulnerabilities we can detect?"
        } else if lowercaseQuery.contains("wireless") || lowercaseQuery.contains("wifi") {
            if featureCoordinator.activePremiumFeatures.contains(.wirelessAttacks) {
                return "Our wireless scanning feature can detect common WiFi vulnerabilities like weak passwords, WPS vulnerabilities, and misconfigured access points. Would you like to start a wireless scan?"
            } else {
                return "Wireless scanning is a premium feature. Would you like to learn more about our premium features?"
            }
        } else if lowercaseQuery.contains("predict") || lowercaseQuery.contains("ai") {
            if featureCoordinator.activePremiumFeatures.contains(.aiPrediction) {
                return "Our AI prediction system can analyze target systems and predict likely open ports and vulnerabilities based on historical data and machine learning models. Would you like me to explain how it works?"
            } else {
                return "AI-powered prediction is a premium feature that helps you identify potential vulnerabilities before scanning. Would you like to learn more?"
            }
        } else if lowercaseQuery.contains("help") || lowercaseQuery.contains("tutorial") {
            return """
            Here are some things I can help you with:
            1. Understanding scan results
            2. Identifying security vulnerabilities
            3. Recommending security improvements
            4. Explaining premium features
            5. Providing scanning tips
            
            What would you like to know more about?
            """
        }
        
        return "I'm not sure about that. Would you like me to explain our main features or help you with a specific scanning task?"
    }
    
    private func handleNewScanResult(_ result: ScanResult) {
        let summary = """
        I noticed you just completed a scan! Here's a quick summary:
        
        Target: \(result.target)
        Duration: \(String(format: "%.2f", result.scanDuration))s
        Open Ports: \(result.results.count)
        
        Would you like me to analyze these results in detail?
        """
        
        let botMessage = Message(content: summary, isUser: false, timestamp: Date())
        messages.append(botMessage)
    }
}

struct ChatbotView: View {
    @StateObject private var viewModel = ChatViewModel()
    @Environment(\.colorScheme) private var colorScheme
    
    var body: some View {
        VStack {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(viewModel.messages) { message in
                            MessageBubble(message: message)
                                .id(message.id)
                        }
                        
                        if viewModel.isTyping {
                            TypingIndicator()
                        }
                    }
                    .padding()
                }
                .onChange(of: viewModel.messages) { _ in
                    if let lastMessage = viewModel.messages.last {
                        withAnimation {
                            proxy.scrollTo(lastMessage.id)
                        }
                    }
                }
            }
            
            Divider()
            
            HStack {
                TextField(NSLocalizedString("type_message", comment: ""), text: $viewModel.inputMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .submitLabel(.send)
                    .onSubmit {
                        viewModel.sendMessage()
                    }
                
                Button(action: viewModel.sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                }
                .disabled(viewModel.inputMessage.isEmpty)
            }
            .padding()
        }
        .navigationTitle("Security Assistant")
    }
}

struct MessageBubble: View {
    let message: Message
    @Environment(\.colorScheme) private var colorScheme
    
    var body: some View {
        HStack {
            if message.isUser { Spacer() }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(12)
                    .background(message.isUser ? Color.blue : Color(UIColor.secondarySystemBackground))
                    .foregroundColor(message.isUser ? .white : .primary)
                    .cornerRadius(16)
                
                Text(message.timestamp, style: .time)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            if !message.isUser { Spacer() }
        }
    }
}

struct TypingIndicator: View {
    @State private var phase = 0
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .fill(Color.secondary)
                    .frame(width: 8, height: 8)
                    .scaleEffect(phase == index ? 1.2 : 0.8)
                    .animation(.easeInOut(duration: 0.5).repeatForever(), value: phase)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .onAppear {
            withAnimation {
                phase = (phase + 1) % 3
            }
        }
    }
}
