// swift-tools-version: 6.2
// Package manifest for the NEMO macOS companion (menu bar app + IPC library).

import PackageDescription

let package = Package(
    name: "NEMO",
    platforms: [
        .macOS(.v15),
    ],
    products: [
        .library(name: "NEMOIPC", targets: ["NEMOIPC"]),
        .library(name: "NEMODiscovery", targets: ["NEMODiscovery"]),
        .executable(name: "NEMO", targets: ["NEMO"]),
        .executable(name: "nemo-mac", targets: ["NEMOMacCLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/orchetect/MenuBarExtraAccess", exact: "1.2.2"),
        .package(url: "https://github.com/swiftlang/swift-subprocess.git", from: "0.1.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.8.0"),
        .package(url: "https://github.com/sparkle-project/Sparkle", from: "2.8.1"),
        .package(url: "https://github.com/steipete/Peekaboo.git", branch: "main"),
        .package(path: "../shared/NEMOKit"),
        .package(path: "../../Swabble"),
    ],
    targets: [
        .target(
            name: "NEMOIPC",
            dependencies: [],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "NEMODiscovery",
            dependencies: [
                .product(name: "NEMOKit", package: "NEMOKit"),
            ],
            path: "Sources/NEMODiscovery",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "NEMO",
            dependencies: [
                "NEMOIPC",
                "NEMODiscovery",
                .product(name: "NEMOKit", package: "NEMOKit"),
                .product(name: "NEMOChatUI", package: "NEMOKit"),
                .product(name: "NEMOProtocol", package: "NEMOKit"),
                .product(name: "SwabbleKit", package: "swabble"),
                .product(name: "MenuBarExtraAccess", package: "MenuBarExtraAccess"),
                .product(name: "Subprocess", package: "swift-subprocess"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Sparkle", package: "Sparkle"),
                .product(name: "PeekabooBridge", package: "Peekaboo"),
                .product(name: "PeekabooAutomationKit", package: "Peekaboo"),
            ],
            exclude: [
                "Resources/Info.plist",
            ],
            resources: [
                .copy("Resources/NEMO.icns"),
                .copy("Resources/DeviceModels"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "NEMOMacCLI",
            dependencies: [
                "NEMODiscovery",
                .product(name: "NEMOKit", package: "NEMOKit"),
                .product(name: "NEMOProtocol", package: "NEMOKit"),
            ],
            path: "Sources/NEMOMacCLI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "NEMOIPCTests",
            dependencies: [
                "NEMOIPC",
                "NEMO",
                "NEMODiscovery",
                .product(name: "NEMOProtocol", package: "NEMOKit"),
                .product(name: "SwabbleKit", package: "swabble"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
