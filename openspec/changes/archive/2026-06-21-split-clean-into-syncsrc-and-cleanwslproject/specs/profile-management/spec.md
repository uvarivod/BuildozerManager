## REMOVED Requirements

### Requirement: Profile has delete_exclusions field
**Reason**: SyncSRC and CleanWSLProject both use hardcoded behavior (SyncSRC always preserves `.buildozer`, CleanWSLProject always removes it), making the configurable exclusion list unnecessary.
**Migration**: Existing saved profiles that contain the `delete_exclusions` field will load successfully — the field is ignored and stripped on next save.
