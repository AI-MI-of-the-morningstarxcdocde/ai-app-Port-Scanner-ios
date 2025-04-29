import SwiftUI
import WidgetKit

struct PortScannerWidgetEntry: TimelineEntry {
    let date: Date
    let scanProgress: Int
    let openPorts: Int
}

struct DynamicPortScannerWidgetProvider: TimelineProvider {
    func placeholder(in context: Context) -> PortScannerWidgetEntry {
        PortScannerWidgetEntry(date: Date(), scanProgress: 0, openPorts: 0)
    }

    func getSnapshot(in context: Context, completion: @escaping (PortScannerWidgetEntry) -> Void) {
        let entry = PortScannerWidgetEntry(date: Date(), scanProgress: 50, openPorts: 5)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<PortScannerWidgetEntry>) -> Void) {
        var entries: [PortScannerWidgetEntry] = []
        for progress in stride(from: 0, through: 100, by: 10) {
            let entry = PortScannerWidgetEntry(date: Date().addingTimeInterval(Double(progress) * 60), scanProgress: progress, openPorts: progress / 10)
            entries.append(entry)
        }
        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
}

struct PortScannerWidgetView: View {
    var entry: PortScannerWidgetProvider.Entry

    var body: some View {
        VStack {
            Text("Port Scanner Progress")
                .font(.headline)
            Text("Progress: \(entry.scanProgress)%")
            Text("Open Ports: \(entry.openPorts)")
        }
        .padding()
    }
}

@main
struct DynamicPortScannerWidget: Widget {
    let kind: String = "DynamicPortScannerWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: DynamicPortScannerWidgetProvider()) { entry in
            PortScannerWidgetView(entry: entry)
        }
        .configurationDisplayName("Dynamic Port Scanner")
        .description("View real-time scan progress and open ports dynamically.")
    }
}

struct PortScannerWidget_Previews: PreviewProvider {
    static var previews: some View {
        PortScannerWidgetView(entry: PortScannerWidgetEntry(date: Date(), scanProgress: 50, openPorts: 5))
            .previewContext(WidgetPreviewContext(family: .systemSmall))
    }
}