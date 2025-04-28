import XCTest
@testable import PortScanner

class PortScannerTests: XCTestCase {
    func testPortScanning() async throws {
        let scanner = PortScanner()
        let results = try await scanner.scan(ip: "192.168.1.1", ports: "1-1000")
        XCTAssertNotNil(results)
    }
    
    func testAIPrediction() async throws {
        let ai = AIPredictor()
        let prediction = try await ai.predictVulnerabilities(for: "192.168.1.1")
        XCTAssertNotNil(prediction)
    }
}