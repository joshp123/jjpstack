# T3 Code's server settings, the same on every machine that runs T3. Claude
# reads the T3 override prompt by file; Codex runs through t3-codex, which reads
# the same file. The policy is merged into ~/.t3/userdata/settings.json; T3 owns
# every other key, and watches the file.
{ pkgs, lib, overrides, codexBinaryPath ? null }:

let
  t3Codex = pkgs.writeShellScript "t3-codex" (
    lib.replaceStrings [ "@jq@" "@overrides@" ] [ "${pkgs.jq}/bin/jq" overrides ]
      (builtins.readFile ./t3-codex.sh)
  );
in
{
  inherit t3Codex;
  policy = (pkgs.formats.json { }).generate "t3-settings-policy.json" {
    # Josh, 31 Oct 2026: "no compact when away".
    idleCompaction = "off";
    # Also gates T3's hourly fetch of its model list from GitHub, which is how
    # a new model appears on its release day rather than with T3's next release.
    enableProviderUpdateChecks = true;
    linkedEnvironmentsEnabled = true;
    # Josh, 12 Nov 2026: "ok back to opus 5.5. and ensure we DONT stay stuck
    # on fast mode". Change the default here: each switch or deploy puts this
    # value back over one picked in the app.
    defaultModelSelection = {
      instanceId = "claudeAgent";
      model = "claude-opus-5-5";
      options = [
        { id = "effort"; value = "medium"; }
        { id = "fastMode"; value = false; }
      ];
    };
    providerInstances = {
      claudeAgent = {
        driver = "claudeAgent";
        config = {
          launchArgs = "--append-system-prompt-file ${overrides}";
          idleCompaction = "off";
        };
      };
      codex = {
        driver = "codex";
        config = {
          binaryPath = if codexBinaryPath == null then "${t3Codex}" else codexBinaryPath;
          launchArgs = "";
        };
      };
    };
  };
}
