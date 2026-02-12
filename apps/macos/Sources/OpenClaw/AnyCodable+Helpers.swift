import NEMOKit
import NEMOProtocol
import Foundation

// Prefer the NEMOKit wrapper to keep gateway request payloads consistent.
typealias AnyCodable = NEMOKit.AnyCodable
typealias InstanceIdentity = NEMOKit.InstanceIdentity

extension AnyCodable {
    var stringValue: String? { self.value as? String }
    var boolValue: Bool? { self.value as? Bool }
    var intValue: Int? { self.value as? Int }
    var doubleValue: Double? { self.value as? Double }
    var dictionaryValue: [String: AnyCodable]? { self.value as? [String: AnyCodable] }
    var arrayValue: [AnyCodable]? { self.value as? [AnyCodable] }

    var foundationValue: Any {
        switch self.value {
        case let dict as [String: AnyCodable]:
            dict.mapValues { $0.foundationValue }
        case let array as [AnyCodable]:
            array.map(\.foundationValue)
        default:
            self.value
        }
    }
}

extension NEMOProtocol.AnyCodable {
    var stringValue: String? { self.value as? String }
    var boolValue: Bool? { self.value as? Bool }
    var intValue: Int? { self.value as? Int }
    var doubleValue: Double? { self.value as? Double }
    var dictionaryValue: [String: NEMOProtocol.AnyCodable]? { self.value as? [String: NEMOProtocol.AnyCodable] }
    var arrayValue: [NEMOProtocol.AnyCodable]? { self.value as? [NEMOProtocol.AnyCodable] }

    var foundationValue: Any {
        switch self.value {
        case let dict as [String: NEMOProtocol.AnyCodable]:
            dict.mapValues { $0.foundationValue }
        case let array as [NEMOProtocol.AnyCodable]:
            array.map(\.foundationValue)
        default:
            self.value
        }
    }
}
