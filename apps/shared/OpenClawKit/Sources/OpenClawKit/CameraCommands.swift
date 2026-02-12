import Foundation

public enum NEMOCameraCommand: String, Codable, Sendable {
    case list = "camera.list"
    case snap = "camera.snap"
    case clip = "camera.clip"
}

public enum NEMOCameraFacing: String, Codable, Sendable {
    case back
    case front
}

public enum NEMOCameraImageFormat: String, Codable, Sendable {
    case jpg
    case jpeg
}

public enum NEMOCameraVideoFormat: String, Codable, Sendable {
    case mp4
}

public struct NEMOCameraSnapParams: Codable, Sendable, Equatable {
    public var facing: NEMOCameraFacing?
    public var maxWidth: Int?
    public var quality: Double?
    public var format: NEMOCameraImageFormat?
    public var deviceId: String?
    public var delayMs: Int?

    public init(
        facing: NEMOCameraFacing? = nil,
        maxWidth: Int? = nil,
        quality: Double? = nil,
        format: NEMOCameraImageFormat? = nil,
        deviceId: String? = nil,
        delayMs: Int? = nil)
    {
        self.facing = facing
        self.maxWidth = maxWidth
        self.quality = quality
        self.format = format
        self.deviceId = deviceId
        self.delayMs = delayMs
    }
}

public struct NEMOCameraClipParams: Codable, Sendable, Equatable {
    public var facing: NEMOCameraFacing?
    public var durationMs: Int?
    public var includeAudio: Bool?
    public var format: NEMOCameraVideoFormat?
    public var deviceId: String?

    public init(
        facing: NEMOCameraFacing? = nil,
        durationMs: Int? = nil,
        includeAudio: Bool? = nil,
        format: NEMOCameraVideoFormat? = nil,
        deviceId: String? = nil)
    {
        self.facing = facing
        self.durationMs = durationMs
        self.includeAudio = includeAudio
        self.format = format
        self.deviceId = deviceId
    }
}
