import HomeKit

class HomeKitIntegration: NSObject, ObservableObject, HMHomeManagerDelegate {
    @Published var homes: [HMHome] = []

    private var homeManager: HMHomeManager

    override init() {
        self.homeManager = HMHomeManager()
        super.init()
        self.homeManager.delegate = self
    }

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        self.homes = manager.homes
    }

    func scanHomeKitDevices() {
        for home in homes {
            for accessory in home.accessories {
                print("Accessory: \(accessory.name), Category: \(accessory.category.localizedDescription)")
            }
        }
    }
}