package ai.nemo.android.protocol

import org.junit.Assert.assertEquals
import org.junit.Test

class NEMOProtocolConstantsTest {
  @Test
  fun canvasCommandsUseStableStrings() {
    assertEquals("canvas.present", NEMOCanvasCommand.Present.rawValue)
    assertEquals("canvas.hide", NEMOCanvasCommand.Hide.rawValue)
    assertEquals("canvas.navigate", NEMOCanvasCommand.Navigate.rawValue)
    assertEquals("canvas.eval", NEMOCanvasCommand.Eval.rawValue)
    assertEquals("canvas.snapshot", NEMOCanvasCommand.Snapshot.rawValue)
  }

  @Test
  fun a2uiCommandsUseStableStrings() {
    assertEquals("canvas.a2ui.push", NEMOCanvasA2UICommand.Push.rawValue)
    assertEquals("canvas.a2ui.pushJSONL", NEMOCanvasA2UICommand.PushJSONL.rawValue)
    assertEquals("canvas.a2ui.reset", NEMOCanvasA2UICommand.Reset.rawValue)
  }

  @Test
  fun capabilitiesUseStableStrings() {
    assertEquals("canvas", NEMOCapability.Canvas.rawValue)
    assertEquals("camera", NEMOCapability.Camera.rawValue)
    assertEquals("screen", NEMOCapability.Screen.rawValue)
    assertEquals("voiceWake", NEMOCapability.VoiceWake.rawValue)
  }

  @Test
  fun screenCommandsUseStableStrings() {
    assertEquals("screen.record", NEMOScreenCommand.Record.rawValue)
  }
}
