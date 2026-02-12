// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "NEMOKit",
    platforms: [
        .iOS(.v18),
        .macOS(.v15),
    ],
    products: [
        .library(name: "NEMOProtocol", targets: ["NEMOProtocol"]),
        .library(name: "NEMOKit", targets: ["NEMOKit"]),
        .library(name: "NEMOChatUI", targets: ["NEMOChatUI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/steipete/ElevenLabsKit", exact: "0.1.0"),
        .package(url: "https://github.com/gonzalezreal/textual", exact: "0.3.1"),
    ],
    targets: [
        .target(
            name: "NEMOProtocol",
            path: "Sources/NEMOProtocol",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "NEMOKit",
            dependencies: [
                "NEMOProtocol",
                .product(name: "ElevenLabsKit", package: "ElevenLabsKit"),
            ],
            path: "Sources/NEMOKit",
            resources: [
                .process("Resources"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "NEMOChatUI",
            dependencies: [
                "NEMOKit",
                .product(
                    name: "Textual",
                    package: "textual",
                    condition: .when(platforms: [.macOS, .iOS])),
            ],
            path: "Sources/NEMOChatUI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "NEMOKitTests",
            dependencies: ["NEMOKit", "NEMOChatUI"],
            path: "Tests/NEMOKitTests",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
