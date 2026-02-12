import Foundation

public enum NEMODeviceCommand: String, Codable, Sendable {
    case status = "device.status"
    case info = "device.info"
}

public enum NEMOBatteryState: String, Codable, Sendable {
    case unknown
    case unplugged
    case charging
    case full
}

public enum NEMOThermalState: String, Codable, Sendable {
    case nominal
    case fair
    case serious
    case critical
}

public enum NEMONetworkPathStatus: String, Codable, Sendable {
    case satisfied
    case unsatisfied
    case requiresConnection
}

public enum NEMONetworkInterfaceType: String, Codable, Sendable {
    case wifi
    case cellular
    case wired
    case other
}

public struct NEMOBatteryStatusPayload: Codable, Sendable, Equatable {
    public var level: Double?
    public var state: NEMOBatteryState
    public var lowPowerModeEnabled: Bool

    public init(level: Double?, state: NEMOBatteryState, lowPowerModeEnabled: Bool) {
        self.level = level
        self.state = state
        self.lowPowerModeEnabled = lowPowerModeEnabled
    }
}

public struct NEMOThermalStatusPayload: Codable, Sendable, Equatable {
    public var state: NEMOThermalState

    public init(state: NEMOThermalState) {
        self.state = state
    }
}

public struct NEMOStorageStatusPayload: Codable, Sendable, Equatable {
    public var totalBytes: Int64
    public var freeBytes: Int64
    public var usedBytes: Int64

    public init(totalBytes: Int64, freeBytes: Int64, usedBytes: Int64) {
        self.totalBytes = totalBytes
        self.freeBytes = freeBytes
        self.usedBytes = usedBytes
    }
}

public struct NEMONetworkStatusPayload: Codable, Sendable, Equatable {
    public var status: NEMONetworkPathStatus
    public var isExpensive: Bool
    public var isConstrained: Bool
    public var interfaces: [NEMONetworkInterfaceType]

    public init(
        status: NEMONetworkPathStatus,
        isExpensive: Bool,
        isConstrained: Bool,
        interfaces: [NEMONetworkInterfaceType])
    {
        self.status = status
        self.isExpensive = isExpensive
        self.isConstrained = isConstrained
        self.interfaces = interfaces
    }
}

public struct NEMODeviceStatusPayload: Codable, Sendable, Equatable {
    public var battery: NEMOBatteryStatusPayload
    public var thermal: NEMOThermalStatusPayload
    public var storage: NEMOStorageStatusPayload
    public var network: NEMONetworkStatusPayload
    public var uptimeSeconds: Double

    public init(
        battery: NEMOBatteryStatusPayload,
        thermal: NEMOThermalStatusPayload,
        storage: NEMOStorageStatusPayload,
        network: NEMONetworkStatusPayload,
        uptimeSeconds: Double)
    {
        self.battery = battery
        self.thermal = thermal
        self.storage = storage
        self.network = network
        self.uptimeSeconds = uptimeSeconds
    }
}

public struct NEMODeviceInfoPayload: Codable, Sendable, Equatable {
    public var deviceName: String
    public var modelIdentifier: String
    public var systemName: String
    public var systemVersion: String
    public var appVersion: String
    public var appBuild: String
    public var locale: String

    public init(
        deviceName: String,
        modelIdentifier: String,
        systemName: String,
        systemVersion: String,
        appVersion: String,
        appBuild: String,
        locale: String)
    {
        self.deviceName = deviceName
        self.modelIdentifier = modelIdentifier
        self.systemName = systemName
        self.systemVersion = systemVersion
        self.appVersion = appVersion
        self.appBuild = appBuild
        self.locale = locale
    }
}
