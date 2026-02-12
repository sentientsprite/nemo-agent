import Foundation

// Stable identifier used for both the macOS LaunchAgent label and Nix-managed defaults suite.
// nix-nemo writes app defaults into this suite to survive app bundle identifier churn.
let launchdLabel = "ai.nemo.mac"
let gatewayLaunchdLabel = "ai.nemo.gateway"
let onboardingVersionKey = "nemo.onboardingVersion"
let onboardingSeenKey = "nemo.onboardingSeen"
let currentOnboardingVersion = 7
let pauseDefaultsKey = "nemo.pauseEnabled"
let iconAnimationsEnabledKey = "nemo.iconAnimationsEnabled"
let swabbleEnabledKey = "nemo.swabbleEnabled"
let swabbleTriggersKey = "nemo.swabbleTriggers"
let voiceWakeTriggerChimeKey = "nemo.voiceWakeTriggerChime"
let voiceWakeSendChimeKey = "nemo.voiceWakeSendChime"
let showDockIconKey = "nemo.showDockIcon"
let defaultVoiceWakeTriggers = ["nemo"]
let voiceWakeMaxWords = 32
let voiceWakeMaxWordLength = 64
let voiceWakeMicKey = "nemo.voiceWakeMicID"
let voiceWakeMicNameKey = "nemo.voiceWakeMicName"
let voiceWakeLocaleKey = "nemo.voiceWakeLocaleID"
let voiceWakeAdditionalLocalesKey = "nemo.voiceWakeAdditionalLocaleIDs"
let voicePushToTalkEnabledKey = "nemo.voicePushToTalkEnabled"
let talkEnabledKey = "nemo.talkEnabled"
let iconOverrideKey = "nemo.iconOverride"
let connectionModeKey = "nemo.connectionMode"
let remoteTargetKey = "nemo.remoteTarget"
let remoteIdentityKey = "nemo.remoteIdentity"
let remoteProjectRootKey = "nemo.remoteProjectRoot"
let remoteCliPathKey = "nemo.remoteCliPath"
let canvasEnabledKey = "nemo.canvasEnabled"
let cameraEnabledKey = "nemo.cameraEnabled"
let systemRunPolicyKey = "nemo.systemRunPolicy"
let systemRunAllowlistKey = "nemo.systemRunAllowlist"
let systemRunEnabledKey = "nemo.systemRunEnabled"
let locationModeKey = "nemo.locationMode"
let locationPreciseKey = "nemo.locationPreciseEnabled"
let peekabooBridgeEnabledKey = "nemo.peekabooBridgeEnabled"
let deepLinkKeyKey = "nemo.deepLinkKey"
let modelCatalogPathKey = "nemo.modelCatalogPath"
let modelCatalogReloadKey = "nemo.modelCatalogReload"
let cliInstallPromptedVersionKey = "nemo.cliInstallPromptedVersion"
let heartbeatsEnabledKey = "nemo.heartbeatsEnabled"
let debugPaneEnabledKey = "nemo.debugPaneEnabled"
let debugFileLogEnabledKey = "nemo.debug.fileLogEnabled"
let appLogLevelKey = "nemo.debug.appLogLevel"
let voiceWakeSupported: Bool = ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 26
