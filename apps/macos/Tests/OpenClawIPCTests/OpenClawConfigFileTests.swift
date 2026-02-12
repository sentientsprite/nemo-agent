import Foundation
import Testing
@testable import NEMO

@Suite(.serialized)
struct NEMOConfigFileTests {
    @Test
    func configPathRespectsEnvOverride() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("nemo-config-\(UUID().uuidString)")
            .appendingPathComponent("nemo.json")
            .path

        await TestIsolation.withEnvValues(["NEMO_CONFIG_PATH": override]) {
            #expect(NEMOConfigFile.url().path == override)
        }
    }

    @MainActor
    @Test
    func remoteGatewayPortParsesAndMatchesHost() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("nemo-config-\(UUID().uuidString)")
            .appendingPathComponent("nemo.json")
            .path

        await TestIsolation.withEnvValues(["NEMO_CONFIG_PATH": override]) {
            NEMOConfigFile.saveDict([
                "gateway": [
                    "remote": [
                        "url": "ws://gateway.ts.net:19999",
                    ],
                ],
            ])
            #expect(NEMOConfigFile.remoteGatewayPort() == 19999)
            #expect(NEMOConfigFile.remoteGatewayPort(matchingHost: "gateway.ts.net") == 19999)
            #expect(NEMOConfigFile.remoteGatewayPort(matchingHost: "gateway") == 19999)
            #expect(NEMOConfigFile.remoteGatewayPort(matchingHost: "other.ts.net") == nil)
        }
    }

    @MainActor
    @Test
    func setRemoteGatewayUrlPreservesScheme() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("nemo-config-\(UUID().uuidString)")
            .appendingPathComponent("nemo.json")
            .path

        await TestIsolation.withEnvValues(["NEMO_CONFIG_PATH": override]) {
            NEMOConfigFile.saveDict([
                "gateway": [
                    "remote": [
                        "url": "wss://old-host:111",
                    ],
                ],
            ])
            NEMOConfigFile.setRemoteGatewayUrl(host: "new-host", port: 2222)
            let root = NEMOConfigFile.loadDict()
            let url = ((root["gateway"] as? [String: Any])?["remote"] as? [String: Any])?["url"] as? String
            #expect(url == "wss://new-host:2222")
        }
    }

    @Test
    func stateDirOverrideSetsConfigPath() async {
        let dir = FileManager().temporaryDirectory
            .appendingPathComponent("nemo-state-\(UUID().uuidString)", isDirectory: true)
            .path

        await TestIsolation.withEnvValues([
            "NEMO_CONFIG_PATH": nil,
            "NEMO_STATE_DIR": dir,
        ]) {
            #expect(NEMOConfigFile.stateDirURL().path == dir)
            #expect(NEMOConfigFile.url().path == "\(dir)/nemo.json")
        }
    }
}
