type StateDirEnvSnapshot = {
  nemoStateDir: string | undefined;
  nemoAgentStateDir: string | undefined;
};

export function snapshotStateDirEnv(): StateDirEnvSnapshot {
  return {
    nemoStateDir: process.env.NEMO_STATE_DIR,
    nemoAgentStateDir: process.env.NEMO_STATE_DIR,
  };
}

export function restoreStateDirEnv(snapshot: StateDirEnvSnapshot): void {
  if (snapshot.nemoStateDir === undefined) {
    delete process.env.NEMO_STATE_DIR;
  } else {
    process.env.NEMO_STATE_DIR = snapshot.nemoStateDir;
  }
  if (snapshot.nemoAgentStateDir === undefined) {
    delete process.env.NEMO_STATE_DIR;
  } else {
    process.env.NEMO_STATE_DIR = snapshot.nemoAgentStateDir;
  }
}

export function setStateDirEnv(stateDir: string): void {
  process.env.NEMO_STATE_DIR = stateDir;
  delete process.env.NEMO_STATE_DIR;
}
