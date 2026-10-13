-- OBS built-in Lua integration. Manual button only; no automatic recording on load.
obs = obslua
local running = false
local previous_scene = nil
local muted_sources = {}
local test_scene = nil
local started = false
local root = script_path() .. '../../'

function script_description()
  return 'Wonder Chess qualification: records ONLY the synthetic reference board for 8 seconds. Mutes global audio during the test and restores the prior scene/mute states after recording stops. No desktop capture, microphone, network, or streaming.'
end

local function restore()
  if previous_scene then
    obs.obs_frontend_set_current_scene(previous_scene)
    obs.obs_source_release(previous_scene)
    previous_scene = nil
  end
  for _, entry in ipairs(muted_sources) do
    obs.obs_source_set_muted(entry.source, entry.muted)
    obs.obs_source_release(entry.source)
  end
  muted_sources = {}
  if test_scene then obs.obs_scene_release(test_scene); test_scene = nil end
  running = false
end

local function finish()
  obs.timer_remove(finish)
  if started and obs.obs_frontend_recording_active() then obs.obs_frontend_recording_stop() end
end

local function event(code)
  if not running then return end
  if code == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED then
    started = true
    obs.timer_add(finish, 8000)
  elseif code == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED then
    local path = obs.obs_frontend_get_last_recording()
    local file = io.open(root .. 'reports/pipeline-tools-20260921/obs-recording-path.txt', 'w')
    if file then file:write(path or 'unavailable'); file:close() end
    restore()
  end
end

local function timeout()
  obs.timer_remove(timeout)
  if running and not started then restore() end
end

function run_test()
  if running or obs.obs_frontend_recording_active() or obs.obs_frontend_streaming_active() then
    obs.script_log(obs.LOG_WARNING, 'Busy: test did not start.'); return false
  end
  local path = root .. 'support/tools/pipeline/fixtures/reference-board.png'
  local check = io.open(path,'rb')
  if not check then obs.script_log(obs.LOG_ERROR,'Missing fixture'); return false end
  check:close()
  previous_scene = obs.obs_frontend_get_current_scene()
  for channel = 1, 5 do
    local source = obs.obs_get_output_source(channel)
    if source then
      table.insert(muted_sources,{source=source,muted=obs.obs_source_muted(source)})
      obs.obs_source_set_muted(source,true)
    end
  end
  test_scene = obs.obs_scene_create_private('WC synthetic qualification')
  local settings = obs.obs_data_create()
  obs.obs_data_set_string(settings,'file',path)
  local source = obs.obs_source_create_private('image_source','Qualification board',settings)
  obs.obs_data_release(settings)
  if not source then restore(); return false end
  obs.obs_scene_add(test_scene,source)
  obs.obs_source_release(source)
  obs.obs_frontend_set_current_scene(obs.obs_scene_get_source(test_scene))
  running = true; started = false
  obs.timer_add(timeout,15000)
  obs.obs_frontend_recording_start()
  return true
end

function script_properties()
  local props=obs.obs_properties_create()
  obs.obs_properties_add_button(props,'run','Record synthetic fixture (8 seconds)',run_test)
  return props
end

function script_load(settings) obs.obs_frontend_add_event_callback(event) end
function script_unload()
  obs.timer_remove(finish); obs.timer_remove(timeout)
  if running and started and obs.obs_frontend_recording_active() then obs.obs_frontend_recording_stop() end
  -- Avoid unmuting global audio until OBS has stopped.
  if not obs.obs_frontend_recording_active() then restore() end
end
