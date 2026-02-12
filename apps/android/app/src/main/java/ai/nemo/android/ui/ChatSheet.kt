package ai.nemo.android.ui

import androidx.compose.runtime.Composable
import ai.nemo.android.MainViewModel
import ai.nemo.android.ui.chat.ChatSheetContent

@Composable
fun ChatSheet(viewModel: MainViewModel) {
  ChatSheetContent(viewModel = viewModel)
}
