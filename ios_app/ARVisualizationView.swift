import SwiftUI
import ARKit
import RealityKit
import Combine

struct NetworkNode: Identifiable, Hashable {
    let id: UUID = UUID()
    let ip: String
    let ports: [Int]
    let type: NodeType
    var position: SIMD3<Float>
    var connections: [String]
    var vulnerabilities: [String]
    var riskLevel: Int
    
    enum NodeType {
        case target
        case openPort
        case vulnerability
        case service
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: NetworkNode, rhs: NetworkNode) -> Bool {
        lhs.id == rhs.id
    }
}

class ARVisualizationViewModel: ObservableObject {
    @Published var nodes: [NetworkNode] = []
    @Published var selectedNode: NetworkNode?
    @Published var isScanning = false
    @Published var showInfo = false
    @Published var error: Error?
    
    private var cancellables = Set<AnyCancellable>()
    
    func loadNetworkData() {
        isScanning = true
        // Simulated network data loading
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.createSampleNetworkData()
            self.isScanning = false
            self.showInfo = true
        }
    }
    
    private func createSampleNetworkData() {
        let target = NetworkNode(
            ip: "192.168.1.1",
            ports: [80, 443, 22],
            type: .target,
            position: SIMD3<Float>(0, 0, -1),
            connections: ["192.168.1.2", "192.168.1.3"],
            vulnerabilities: ["CVE-2021-1234"],
            riskLevel: 3
        )
        
        let node1 = NetworkNode(
            ip: "192.168.1.2",
            ports: [80],
            type: .service,
            position: SIMD3<Float>(-0.5, 0.3, -1),
            connections: ["192.168.1.1"],
            vulnerabilities: [],
            riskLevel: 1
        )
        
        let node2 = NetworkNode(
            ip: "192.168.1.3",
            ports: [443, 8080],
            type: .openPort,
            position: SIMD3<Float>(0.5, 0.3, -1),
            connections: ["192.168.1.1"],
            vulnerabilities: ["CVE-2021-5678"],
            riskLevel: 2
        )
        
        nodes = [target, node1, node2]
    }
}

struct ARVisualizationContainerView: View {
    @StateObject private var viewModel = ARVisualizationViewModel()
    @EnvironmentObject private var appCoordinator: AppCoordinator
    
    var body: some View {
        Group {
            if appCoordinator.hasUnlockedFeatures {
                ARVisualizationView(viewModel: viewModel)
            } else {
                PremiumFeatureView(
                    title: "AR Network Visualization",
                    message: "Visualize your network topology in augmented reality with interactive 3D nodes and connections.",
                    action: {
                        NavigationCoordinator.shared.presentSheet(.monetization)
                    }
                )
            }
        }
        .navigationTitle("AR Visualization")
    }
}

struct ARVisualizationView: UIViewRepresentable {
    @ObservedObject var viewModel: ARVisualizationViewModel
    
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Setup AR session
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal]
        arView.session.run(config)
        
        // Add tap gesture
        let tapGesture = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handleTap)
        )
        arView.addGestureRecognizer(tapGesture)
        
        context.coordinator.arView = arView
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {
        context.coordinator.updateNodes(viewModel.nodes)
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(viewModel: viewModel)
    }
    
    class Coordinator: NSObject {
        weak var arView: ARView?
        var viewModel: ARVisualizationViewModel
        var nodeEntities: [UUID: ModelEntity] = [:]
        
        init(viewModel: ARVisualizationViewModel) {
            self.viewModel = viewModel
            super.init()
        }
        
        func updateNodes(_ nodes: [NetworkNode]) {
            guard let arView = arView else { return }
            
            // Clear existing nodes
            nodeEntities.values.forEach { $0.removeFromParent() }
            nodeEntities.removeAll()
            
            // Create new nodes
            for node in nodes {
                let mesh: MeshResource
                let material: SimpleMaterial
                
                switch node.type {
                case .target:
                    mesh = .generateSphere(radius: 0.1)
                    material = SimpleMaterial(color: .red, roughness: 0.5, isMetallic: true)
                case .openPort:
                    mesh = .generateBox(size: 0.08)
                    material = SimpleMaterial(color: .blue, roughness: 0.3, isMetallic: true)
                case .vulnerability:
                    mesh = .generateBox(size: 0.08)
                    material = SimpleMaterial(color: .yellow, roughness: 0.3, isMetallic: true)
                case .service:
                    mesh = .generateBox(size: 0.08)
                    material = SimpleMaterial(color: .green, roughness: 0.3, isMetallic: true)
                }
                
                let entity = ModelEntity(mesh: mesh, materials: [material])
                entity.position = node.position
                
                // Add to scene
                let anchor = AnchorEntity(world: node.position)
                anchor.addChild(entity)
                arView.scene.addAnchor(anchor)
                
                nodeEntities[node.id] = entity
            }
            
            // Draw connections
            drawConnections(nodes)
        }
        
        private func drawConnections(_ nodes: [NetworkNode]) {
            guard let arView = arView else { return }
            
            for node in nodes {
                for connectedIP in node.connections {
                    if let connectedNode = nodes.first(where: { $0.ip == connectedIP }) {
                        let start = node.position
                        let end = connectedNode.position
                        
                        let length = simd_length(end - start)
                        let direction = simd_normalize(end - start)
                        
                        let mesh = MeshResource.generateBox(
                            width: 0.01,
                            height: 0.01,
                            depth: length
                        )
                        let material = SimpleMaterial(
                            color: .white.withAlphaComponent(0.5),
                            roughness: 0.5,
                            isMetallic: false
                        )
                        
                        let connection = ModelEntity(mesh: mesh, materials: [material])
                        connection.position = (start + end) / 2
                        
                        // Calculate rotation to point from start to end
                        let rotation = simd_quatf(from: [0, 0, 1], to: direction)
                        connection.orientation = rotation
                        
                        let anchor = AnchorEntity(world: connection.position)
                        anchor.addChild(connection)
                        arView.scene.addAnchor(anchor)
                    }
                }
            }
        }
        
        @objc func handleTap(_ recognizer: UITapGestureRecognizer) {
            guard let arView = arView else { return }
            
            let location = recognizer.location(in: arView)
            let results = arView.raycast(from: location, allowing: .estimatedPlane, alignment: .horizontal)
            
            if let result = results.first {
                // Add new node at tap location
                let position = result.worldTransform.columns.3
                addNodeAtPosition(SIMD3<Float>(position.x, position.y, position.z))
            }
        }
        
        private func addNodeAtPosition(_ position: SIMD3<Float>) {
            let newNode = NetworkNode(
                ip: "192.168.1.\(Int.random(in: 2...254))",
                ports: [Int.random(in: 1...65535)],
                type: .service,
                position: position,
                connections: [],
                vulnerabilities: [],
                riskLevel: Int.random(in: 1...3)
            )
            
            viewModel.nodes.append(newNode)
            updateNodes(viewModel.nodes)
        }
    }
}

struct NodeInfoView: View {
    let node: NetworkNode
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("IP: \(node.ip)")
                .font(.headline)
            
            Text("Ports: \(node.ports.map(String.init).joined(separator: ", "))")
            
            if !node.vulnerabilities.isEmpty {
                Text("Vulnerabilities:")
                    .font(.headline)
                ForEach(node.vulnerabilities, id: \.self) { vulnerability in
                    Text("• \(vulnerability)")
                        .foregroundColor(.red)
                }
            }
            
            Text("Risk Level: \(node.riskLevel)")
                .foregroundColor(riskLevelColor)
        }
        .padding()
        .background(Color(UIColor.systemBackground))
        .cornerRadius(10)
        .shadow(radius: 5)
    }
    
    private var riskLevelColor: Color {
        switch node.riskLevel {
        case 1: return .green
        case 2: return .yellow
        case 3: return .red
        default: return .gray
        }
    }
}
