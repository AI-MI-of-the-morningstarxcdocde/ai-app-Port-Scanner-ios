import SwiftUI
import ARKit

struct ARVisualizationView: View {
    var body: some View {
        InteractiveARViewContainer()
            .edgesIgnoringSafeArea(.all)
    }
}

struct InteractiveARViewContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> ARSCNView {
        let arView = ARSCNView()
        arView.scene = SCNScene()

        // Add interactive AR elements
        let node = SCNNode()
        node.geometry = SCNSphere(radius: 0.1)
        node.geometry?.firstMaterial?.diffuse.contents = UIColor.blue
        node.position = SCNVector3(0, 0, -0.5)
        arView.scene.rootNode.addChildNode(node)

        let tapGesture = UITapGestureRecognizer(target: context.coordinator, action: #selector(Coordinator.handleTap(_:)))
        arView.addGestureRecognizer(tapGesture)

        return arView
    }

    func updateUIView(_ uiView: ARSCNView, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    class Coordinator: NSObject {
        @objc func handleTap(_ sender: UITapGestureRecognizer) {
            print("AR element tapped!")
        }
    }
}

struct ARVisualizationView_Previews: PreviewProvider {
    static var previews: some View {
        ARVisualizationView()
    }
}
