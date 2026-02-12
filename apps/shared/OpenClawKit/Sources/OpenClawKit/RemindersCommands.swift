import Foundation

public enum NEMORemindersCommand: String, Codable, Sendable {
    case list = "reminders.list"
    case add = "reminders.add"
}

public enum NEMOReminderStatusFilter: String, Codable, Sendable {
    case incomplete
    case completed
    case all
}

public struct NEMORemindersListParams: Codable, Sendable, Equatable {
    public var status: NEMOReminderStatusFilter?
    public var limit: Int?

    public init(status: NEMOReminderStatusFilter? = nil, limit: Int? = nil) {
        self.status = status
        self.limit = limit
    }
}

public struct NEMORemindersAddParams: Codable, Sendable, Equatable {
    public var title: String
    public var dueISO: String?
    public var notes: String?
    public var listId: String?
    public var listName: String?

    public init(
        title: String,
        dueISO: String? = nil,
        notes: String? = nil,
        listId: String? = nil,
        listName: String? = nil)
    {
        self.title = title
        self.dueISO = dueISO
        self.notes = notes
        self.listId = listId
        self.listName = listName
    }
}

public struct NEMOReminderPayload: Codable, Sendable, Equatable {
    public var identifier: String
    public var title: String
    public var dueISO: String?
    public var completed: Bool
    public var listName: String?

    public init(
        identifier: String,
        title: String,
        dueISO: String? = nil,
        completed: Bool,
        listName: String? = nil)
    {
        self.identifier = identifier
        self.title = title
        self.dueISO = dueISO
        self.completed = completed
        self.listName = listName
    }
}

public struct NEMORemindersListPayload: Codable, Sendable, Equatable {
    public var reminders: [NEMOReminderPayload]

    public init(reminders: [NEMOReminderPayload]) {
        self.reminders = reminders
    }
}

public struct NEMORemindersAddPayload: Codable, Sendable, Equatable {
    public var reminder: NEMOReminderPayload

    public init(reminder: NEMOReminderPayload) {
        self.reminder = reminder
    }
}
