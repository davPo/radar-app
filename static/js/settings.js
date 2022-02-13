//
//   Project Horus - Browser-Based Chase Mapper - Settings
//
//   Copyright (C) 2019  Mark Jessop <vk5qi@rfhead.net>
//   Released under GNU GPL v3 or later
//

// Global map settings

// Chase Mapper Configuration Parameters.
// These are dummy values which will be populated on startup.
var radar_config = {
    // Start location for the map (until either a chase car position, or balloon position is available.)
    default_lat: 46,
    default_lon: 6,

    offline_tile_layers: [],
};


function serverSettingsUpdate(data){
    // Accept a json blob of settings data from the client, and update our local store.
    console.log(data)
    radar_config = data;
    // Update a few fields based on this data.
  
    // Range ring settings.
    $('#ringQuantity').val(radar_config.range_ring_quantity.toFixed(0));
    $('#ringSpacing').val(radar_config.range_ring_spacing.toFixed(0));
    $('#ringWeight').val(radar_config.range_ring_weight.toFixed(1));
    $('#ringColorSelect').val(radar_config.range_ring_color);
    $('#ringCustomColor').val(radar_config.range_ring_custom_color);
    $('#rangeRingsEnabled').prop('checked', radar_config.range_rings_enabled);
    
    // Bearing settings
    // $('#bearingLength').val(radar_config.bearing_length.toFixed(0));
    // $('#bearingWeight').val(radar_config.bearing_weight.toFixed(1));
    // $('#bearingColorSelect').val(radar_config.bearing_color);
    // $('#bearingCustomColor').val(radar_config.bearing_custom_color);
    
    // Update version
    $('#version').html(radar_config.version);
}

function clientSettingsUpdate(){
    socket.emit('client_settings_update', radar_config);
};