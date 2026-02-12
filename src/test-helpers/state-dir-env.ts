type StateDirEnvSnapshot = {
  nemoStateDir: string | undefined;
  nemo-agentStateDir: string | undefined;
};

export function snapshotStateDirEnv(): StateDirEnvSnapshot {
  return {
    nemoStateDir: process.env.NEMO_STATE_DIR,
    nemo-agentStateDir: process.env.NEMO_STATE_DIR,
  };
}

export function restoreStateDirEnv(snapshot: StateDirEnvSnapshot): void {
  if (snapshot.nemoStateDir === undefined) {
    delete process.env.NEMO_STATE_DIR;
  } else {
    process.env.NEMO_STATE_DIR = snapshot.nemoStateDir;
  }
  if (snapshot.nemo-agentStateDir === undefined) {
    delete process.env.NEMO_STATE_DIR;
  } else {
    process.env.NEMO_STATE_DIR = snapshot.nemo-agentStateDir;
  }
}

export function setStateDirEnv(stateDir: string): void {
  process.env.NEMO_STATE_DIR = stateDir;
  delete process.env.NEMO_STATE_DIR;
}
