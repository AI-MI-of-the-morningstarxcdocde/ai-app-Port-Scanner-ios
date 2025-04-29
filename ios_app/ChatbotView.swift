import SwiftUI
import Combine

struct ChatbotView: View {
    @State private var userInput: String = ""
    @State private var chatHistory: [String] = []
    @State private var isLoading: Bool = false

    var body: some View {
        VStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(chatHistory, id: \ .self) { message in
                        Text(message)
                            .padding()
                            .background(Color.gray.opacity(0.2))
                            .cornerRadius(8)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding()

            HStack {
                TextField("Type your question here...", text: $userInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: 40)

                if isLoading {
                    ProgressView()
                        .frame(width: 40, height: 40)
                } else {
                    Button(action: sendMessage) {
                        Text("Send")
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
            }
            .padding()
        }
    }

    func sendMessage() {
        guard !userInput.isEmpty else { return }
        chatHistory.append("You: \(userInput)")
        isLoading = true

        // Send the user input to the backend chatbot
        let url = URL(string: "http://localhost:5000/chatbot")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = ["message": userInput]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                if let data = data, let response = try? JSONDecoder().decode(ChatbotResponse.self, from: data) {
                    chatHistory.append("AI: \(response.reply)")
                } else {
                    chatHistory.append("AI: Sorry, I couldn't process your request.")
                }
                userInput = ""
            }
        }.resume()
    }
}

struct ChatbotResponse: Decodable {
    let reply: String
}

struct ChatbotView_Previews: PreviewProvider {
    static var previews: some View {
        ChatbotView()
    }
}
