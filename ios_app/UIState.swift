import SwiftUI

enum LoadingState {
    case idle
    case loading
    case success
    case failure(Error)
    
    var isLoading: Bool {
        if case .loading = self { return true }
        return false
    }
    
    var error: Error? {
        if case .failure(let error) = self { return error }
        return nil
    }
}

enum ViewState<T> {
    case loading
    case empty
    case error(String)
    case loaded(T)
    
    var isLoading: Bool {
        if case .loading = self { return true }
        return false
    }
    
    var errorMessage: String? {
        if case .error(let message) = self { return message }
        return nil
    }
    
    var value: T? {
        if case .loaded(let value) = self { return value }
        return nil
    }
}

struct LoadingView: View {
    let message: String
    
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle())
            Text(message)
                .foregroundColor(.secondary)
        }
    }
}

struct ErrorView: View {
    let message: String
    let retryAction: () -> Void
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 50, height: 50)
                .foregroundColor(.red)
            
            Text("Error")
                .font(.headline)
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            Button(action: retryAction) {
                Text("Try Again")
                    .bold()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct EmptyStateView: View {
    let title: String
    let message: String
    let actionTitle: String?
    let action: (() -> Void)?
    
    init(
        title: String,
        message: String,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil
    ) {
        self.title = title
        self.message = message
        self.actionTitle = actionTitle
        self.action = action
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "tray")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 50, height: 50)
                .foregroundColor(.secondary)
            
            Text(title)
                .font(.headline)
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            if let actionTitle = actionTitle, let action = action {
                Button(action: action) {
                    Text(actionTitle)
                        .bold()
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
        }
        .padding()
    }
}

struct PremiumFeatureView: View {
    let title: String
    let message: String
    let action: () -> Void
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "star.circle.fill")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 60, height: 60)
                .foregroundColor(.yellow)
            
            Text(title)
                .font(.title)
                .bold()
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            Button(action: action) {
                Text("Upgrade to Premium")
                    .bold()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .padding(.horizontal)
        }
        .padding()
    }
}

extension View {
    func loadingOverlay(_ isLoading: Bool, message: String = "Loading...") -> some View {
        self.overlay(
            Group {
                if isLoading {
                    ZStack {
                        Color(.systemBackground)
                            .opacity(0.8)
                        LoadingView(message: message)
                    }
                }
            }
        )
    }
    
    func errorAlert(error: Binding<Error?>, retryAction: (() -> Void)? = nil) -> some View {
        self.alert(isPresented: .constant(error.wrappedValue != nil)) {
            Alert(
                title: Text("Error"),
                message: Text(error.wrappedValue?.localizedDescription ?? "An unknown error occurred"),
                primaryButton: .default(Text("OK")) {
                    error.wrappedValue = nil
                },
                secondaryButton: retryAction == nil ? nil : .default(Text("Retry")) {
                    error.wrappedValue = nil
                    retryAction?()
                }
            )
        }
    }
}