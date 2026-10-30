# data/

**No private or identifiable CCTV footage is committed to this repository.**

Phase 0 ships no media at all. Later phases use:
- a **synthetic** camera adapter (generated frames), and
- **offline file mode** for user-provided, authorized clips.

## Rules
- Do not commit scraped or identifiable CCTV footage, faces, or any personal data.
- Clips and model weights are git-ignored (`data/clips/`, `data/footage/`, `*.pt`, …).
- Every dataset/clip must have documented provenance and a license before use.
- Evaluation splits are by store/camera/time, never adjacent random frames.

## Privacy
No face recognition, biometric identification, or demographic inference. Track
IDs are ephemeral and camera-local. Before any real deployment in Türkiye,
obtain a KVKK legal review (basis, notices, purpose limitation, retention,
access, processors, cross-border transfer).
