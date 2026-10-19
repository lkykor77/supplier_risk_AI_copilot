import Foundation
import PDFKit
import Vision
import AppKit

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data(message.utf8))
    exit(1)
}

guard CommandLine.arguments.count >= 2,
      let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    fail("Cannot read this PDF.")
}
guard !document.isLocked else { fail("Password-protected PDFs are not supported. Export an unlocked copy.") }
guard document.pageCount > 0 && document.pageCount <= 25 else { fail("PDF must contain 1 to 25 pages.") }
var pages: [[String: Any]] = []
var characterCount = 0
for index in 0..<document.pageCount {
    let result: [String: Any] = autoreleasepool {
        guard let page = document.page(at: index) else { fail("Cannot read a PDF page.") }
        let native = (page.string ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let bounds = page.bounds(for: .mediaBox)
        guard bounds.width > 0 && bounds.height > 0 else { fail("Invalid PDF page dimensions.") }
        let scale = min(2200 / bounds.width, 2200 / bounds.height)
        let image = page.thumbnail(of: NSSize(width: bounds.width * scale, height: bounds.height * scale), for: .mediaBox)
        guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fail("Cannot render a PDF page.") }
        if CommandLine.arguments.count >= 3 {
            let directory = URL(fileURLWithPath: CommandLine.arguments[2])
            try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            if let png = NSBitmapImageRep(cgImage: cgImage).representation(using: .png, properties: [:]) {
                try? png.write(to: directory.appendingPathComponent("page-\(index + 1).png"))
            }
        }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = true
        let supported = (try? request.supportedRecognitionLanguages()) ?? []
        let languages = ["en-US", "ko-KR"].filter { supported.contains($0) }
        if !languages.isEmpty { request.recognitionLanguages = languages }
        var ocr = ""
        var confidence: Float = 0
        var warning = ""
        do {
            try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
            let lines = (request.results ?? []).sorted {
                if abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.01 {
                    return $0.boundingBox.midY > $1.boundingBox.midY
                }
                return $0.boundingBox.minX < $1.boundingBox.minX
            }.compactMap { $0.topCandidates(1).first }
            ocr = lines.map { $0.string }.joined(separator: "\n")
            confidence = lines.map { $0.confidence }.min() ?? 0
        } catch {
            warning = "OCR failed on this page. Native text may still be usable."
        }
        let chosen = native.count >= 80 && ocr.count <= Int(Double(native.count) * 1.25) ? "native" : "ocr"
        let mode = ocr.isEmpty ? "native" : chosen
        let text = mode == "native" ? native : ocr
        return ["page": index + 1, "native_text": native, "ocr_text": ocr,
                "mode": mode, "text": text, "minimum_ocr_confidence": confidence,
                "warning": warning.isEmpty && text.isEmpty ? "No readable text found; manual transcription is needed." : warning]
    }
    characterCount += (result["native_text"] as? String ?? "").count + (result["ocr_text"] as? String ?? "").count
    guard characterCount <= 300000 else { fail("Extracted text is too large for this prototype.") }
    pages.append(result)
}
let output: [String: Any] = ["pages": pages, "ocr_engine": "Apple Vision", "native_engine": "PDFKit"]
guard let data = try? JSONSerialization.data(withJSONObject: output) else { fail("Cannot encode extraction output.") }
FileHandle.standardOutput.write(data)
