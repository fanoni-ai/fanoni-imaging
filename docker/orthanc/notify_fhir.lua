-- Fires when a study has been stable for ~60 seconds (all instances received).
-- Posts to the imaging-bridge-bot via the Fanoni FHIR server.
-- Set FANONI_BRIDGE_BOT_URL in orthanc.json or hardcode below for local dev.

local BOT_URL = "http://host.docker.internal:8103/fhir/R4/Bot/imaging-bridge-bot/$execute"
local BOT_TOKEN = ""  -- set via FANONI_BOT_TOKEN env or leave empty for local dev

function OnStableStudy(studyId, tags, metadata)
  local body = '{"orthancStudyId":"' .. studyId .. '","event":"StableStudy","orthancBaseUrl":"http://host.docker.internal:8042"}'

  local headers = {}
  headers["Content-Type"] = "application/json"
  if BOT_TOKEN ~= "" then
    headers["Authorization"] = "Bearer " .. BOT_TOKEN
  end

  local status, response = pcall(function()
    return HttpPost(BOT_URL, body, headers)
  end)

  if not status then
    PrintReceivedDicom()
    -- Non-fatal: Orthanc keeps the study regardless of webhook failure
    SystemLog("imaging-bridge-bot webhook failed for study " .. studyId .. ": " .. tostring(response))
  else
    SystemLog("imaging-bridge-bot notified for study " .. studyId)
  end
end
