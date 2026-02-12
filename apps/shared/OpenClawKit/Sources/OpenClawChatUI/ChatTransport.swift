import Foundation

public enum NEMOChatTransportEvent: Sendable {
    case health(ok: Bool)
    case tick
    case chat(NEMOChatEventPayload)
    case agent(NEMOAgentEventPayload)
    case seqGap
}

public protocol NEMOChatTransport: Sendable {
    func requestHistory(sessionKey: String) async throws -> NEMOChatHistoryPayload
    func sendMessage(
        sessionKey: String,
        message: String,
        thinking: String,
        idempotencyKey: String,
        attachments: [NEMOChatAttachmentPayload]) async throws -> NEMOChatSendResponse

    func abortRun(sessionKey: String, runId: String) async throws
    func listSessions(limit: Int?) async throws -> NEMOChatSessionsListResponse

    func requestHealth(timeoutMs: Int) async throws -> Bool
    func events() -> AsyncStream<NEMOChatTransportEvent>

    func setActiveSessionKey(_ sessionKey: String) async throws
}

extension NEMOChatTransport {
    public func setActiveSessionKey(_: String) async throws {}

    public func abortRun(sessionKey _: String, runId _: String) async throws {
        throw NSError(
            domain: "NEMOChatTransport",
            code: 0,
            userInfo: [NSLocalizedDescriptionKey: "chat.abort not supported by this transport"])
    }

    public func listSessions(limit _: Int?) async throws -> NEMOChatSessionsListResponse {
        throw NSError(
            domain: "NEMOChatTransport",
            code: 0,
            userInfo: [NSLocalizedDescriptionKey: "sessions.list not supported by this transport"])
    }
}
