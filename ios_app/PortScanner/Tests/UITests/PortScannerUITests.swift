import XCTest

class PortScannerUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testMainScanFlow() throws {
        // Test basic scan flow
        let ipField = app.textFields["ipAddressField"]
        XCTAssertTrue(ipField.exists)
        
        ipField.tap()
        ipField.typeText("192.168.1.1")
        
        let scanButton = app.buttons["startScanButton"]
        XCTAssertTrue(scanButton.exists)
        scanButton.tap()
        
        // Verify results appear
        let resultsTable = app.tables["scanResultsTable"]
        XCTAssertTrue(resultsTable.waitForExistence(timeout: 10))
    }
    
    func testPremiumFeatures() throws {
        // Test AR visualization
        app.tabBars.buttons["AR View"].tap()
        XCTAssertTrue(app.buttons["startARButton"].exists)
        
        // Test AI prediction
        app.tabBars.buttons["AI Scan"].tap()
        XCTAssertTrue(app.buttons["startAIPredictionButton"].exists)
    }
}