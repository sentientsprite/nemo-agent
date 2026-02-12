import CoreLocation
import Foundation
import NEMOKit
import UIKit

protocol CameraServicing: Sendable {
    func listDevices() async -> [CameraController.CameraDeviceInfo]
    func snap(params: NEMOCameraSnapParams) async throws -> (format: String, base64: String, width: Int, height: Int)
    func clip(params: NEMOCameraClipParams) async throws -> (format: String, base64: String, durationMs: Int, hasAudio: Bool)
}

protocol ScreenRecordingServicing: Sendable {
    func record(
        screenIndex: Int?,
        durationMs: Int?,
        fps: Double?,
        includeAudio: Bool?,
        outPath: String?) async throws -> String
}

@MainActor
protocol LocationServicing: Sendable {
    func authorizationStatus() -> CLAuthorizationStatus
    func accuracyAuthorization() -> CLAccuracyAuthorization
    func ensureAuthorization(mode: NEMOLocationMode) async -> CLAuthorizationStatus
    func currentLocation(
        params: NEMOLocationGetParams,
        desiredAccuracy: NEMOLocationAccuracy,
        maxAgeMs: Int?,
        timeoutMs: Int?) async throws -> CLLocation
}

protocol DeviceStatusServicing: Sendable {
    func status() async throws -> NEMODeviceStatusPayload
    func info() -> NEMODeviceInfoPayload
}

protocol PhotosServicing: Sendable {
    func latest(params: NEMOPhotosLatestParams) async throws -> NEMOPhotosLatestPayload
}

protocol ContactsServicing: Sendable {
    func search(params: NEMOContactsSearchParams) async throws -> NEMOContactsSearchPayload
    func add(params: NEMOContactsAddParams) async throws -> NEMOContactsAddPayload
}

protocol CalendarServicing: Sendable {
    func events(params: NEMOCalendarEventsParams) async throws -> NEMOCalendarEventsPayload
    func add(params: NEMOCalendarAddParams) async throws -> NEMOCalendarAddPayload
}

protocol RemindersServicing: Sendable {
    func list(params: NEMORemindersListParams) async throws -> NEMORemindersListPayload
    func add(params: NEMORemindersAddParams) async throws -> NEMORemindersAddPayload
}

protocol MotionServicing: Sendable {
    func activities(params: NEMOMotionActivityParams) async throws -> NEMOMotionActivityPayload
    func pedometer(params: NEMOPedometerParams) async throws -> NEMOPedometerPayload
}

extension CameraController: CameraServicing {}
extension ScreenRecordService: ScreenRecordingServicing {}
extension LocationService: LocationServicing {}
