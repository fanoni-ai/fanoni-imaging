-- Fires when a study has been stable for ~60 seconds (all instances received).
-- Notifies the Fanoni FHIR imaging-bridge-bot.
--
-- Configuration is read from the container environment (set in docker/.env):
--   FANONI_BRIDGE_BOT_URL    target $execute URL; leave empty to DISABLE the webhook
--   FANONI_BOT_TOKEN         optional bearer token (sent as Authorization header)
--   FANONI_ORTHANC_BASE_URL  base URL the bot uses to call back into Orthanc

local BOT_URL = os.getenv("FANONI_BRIDGE_BOT_URL") or ""
local BOT_TOKEN = os.getenv("FANONI_BOT_TOKEN") or ""
local ORTHANC_BASE_URL = os.getenv("FANONI_ORTHANC_BASE_URL") or "http://host.docker.internal:8042"

function OnStableStudy(studyId, tags, metadata)
  if BOT_URL == "" then
    return  -- webhook disabled (no URL configured)
  end

  -- %q safely quotes/escapes the values into valid JSON strings.
  local body = string.format(
    '{"orthancStudyId":%q,"event":"StableStudy","orthancBaseUrl":%q}',
    studyId, ORTHANC_BASE_URL
  )

  local headers = {}
  headers["Content-Type"] = "application/json"
  if BOT_TOKEN ~= "" then
    headers["Authorization"] = "Bearer " .. BOT_TOKEN
  end

  local ok, response = pcall(function()
    return HttpPost(BOT_URL, body, headers)
  end)

  if ok then
    SystemLog("imaging-bridge-bot notified for study " .. studyId)
  else
    -- Non-fatal: Orthanc keeps the study regardless of webhook failure.
    SystemLog("imaging-bridge-bot webhook failed for study " .. studyId .. ": " .. tostring(response))
  end
end
