// Set map defaults
var map = new mapboxgl.Map({
  container: 'map', // container id
  style: 'mapbox://styles/mapbox/dark-v10', //hosted style id
  center: [-97.735,30.281], // starting position as [lng, lat]
  zoom: 13, // starting zoom
  attributionControl: false
});

// Create legend
var legendContainer = document.createElement("div");
var legendTitle = document.createElement("h4");
var legend100plus = document.createElement("div");
var legend10plus = document.createElement("div");
var legend3plus = document.createElement("div");
var legendLess3 = document.createElement("div");
var legendUndetermined = document.createElement("div");

// Set content
legendContainer.id = "legend";
legendTitle.innerHTML = "Click to toggle layer";
legend100plus.innerHTML = "<span style='background-color: "+color4+"'></span>100+ units";
legend10plus.innerHTML = "<span style='background-color: "+color3+"'></span>10+ units";
legend3plus.innerHTML = "<span style='background-color: "+color2+"'></span>3+ units";
legendLess3.innerHTML = "<span style='background-color: "+color1+"'></span>1-2 units";
legendUndetermined.innerHTML = "<span style='background-color: "+white+"'></span>Code complaints";

// On click filter
legend100plus.addEventListener('click', function() {
        hideLayer(100,999999);
}, false);

legend10plus.addEventListener('click', function() {
        hideLayer(10,99);
}, false);

legend3plus.addEventListener('click', function() {
        hideLayer(3,9);
}, false);

legendLess3.addEventListener('click', function() {
        hideLayer(1,2);
}, false);

legendUndetermined.addEventListener('click', hideCC);

// Add attribution control
var attributionControl = new mapboxgl.AttributionControl({
	customAttribution: "<a href='https://github.com/funkonaut/find-my-landlord-atx/issues/new/choose'><b>Improve our data</b></a> | <a href='https://github.com/funkonaut/find-my-landlord-atx'>View this project on GitHub</a>"
});
map.addControl(attributionControl);

// Get map control
var bottomRightClass = document.getElementsByClassName("mapboxgl-ctrl-bottom-right");
var bottomRightControl = bottomRightClass[0];

// Add legend inside control
bottomRightControl.insertBefore(legendContainer, bottomRightControl.firstChild);
legendContainer.appendChild(legendTitle);
legendContainer.appendChild(legend100plus);
legendContainer.appendChild(legend10plus);
legendContainer.appendChild(legend3plus);
legendContainer.appendChild(legendLess3);
legendContainer.appendChild(legendUndetermined);

// Probably a cleaner way to do this without globals possibly store in meta data?...
var f1 = ["all"];
var f3 = ["all"];
var f10 = ["all"];
var f100 = ["all"];
function hideLayer(low, high) {
        //New filter on click 
        var filterNum = map.getLayer("allProperties").metadata['mapbox:filter-'+low];
        if (filterNum == "False") {
             eval("f"+low+" = " + "[\"any\",[\">\", ownedColumn, high],[\"<\", ownedColumn, low]];");
             map.getLayer("allProperties").metadata['mapbox:filter-'+low] = "True";    
        }
        // Get rid of current filter on 
        else {
             eval("f"+low+" = " + "[\"all\"];");
             map.getLayer("allProperties").metadata['mapbox:filter-'+low] = "False";    
        };
        map.setFilter("allProperties",["all",f1,f3,f10,f100]);
};

// Add hide code complaint data button
function hideCC() {
        var layer = 'codeComplaints';
        var visibility = map.getLayoutProperty(layer, 'visibility'); 
        // toggle layer visibility by changing the layout object's visibility property
        if (visibility === 'visible') {
                map.setLayoutProperty(layer, 'visibility', 'none');
               // this.className = '';
        } 
        else {
              //  this.className = 'active';
                map.setLayoutProperty(layer, 'visibility', 'visible');
        };
};

// Add navigation
var navigationControl = new mapboxgl.NavigationControl();
map.addControl(navigationControl, "top-right");

map.on("load", function() {
	// Load search keys
	var request = new XMLHttpRequest();
	request.open("GET", searchIndex, true);
	request.onload = function() {
		if (this.status >= 200 && this.status < 400) {
			json = JSON.parse(this.response);

			// Set source data for Code complaints 
			map.addSource("codeData", {
				type: "vector",
				maxzoom: 14, // Allows overzoom
			        url: "mapbox://crcorrell.code_map",//change this	
                               //tiles: [tiles],
				promoteId: propertyIndexColumn
			});
                        // all units url "mapbox://crcorrell.50h5qevk",
			// Set source data 100+ units
			map.addSource("propertyData", {
				type: "vector",
				maxzoom: 14, // Allows overzoom
			        url: "mapbox://crcorrell.50h5qevk",//"mapbox://crcorrell.dud9bgpk",                // crcorrell.7hwbg9l1",//change this	
                               //tiles: [tiles],
				promoteId: propertyIndexColumn
			});
                        //Add code complaint layer
			map.addLayer({
				"id": "codeComplaints",
				"type": "circle",
				"source": "codeData",
				"source-layer": "original",   //change this from map_box
			        "visibility": "none",
                        	"paint": {
					"circle-radius": defaultRadiusCC,
					"circle-color": "rgb(255,255,255)",
					"circle-opacity": defaultOpacityCC,
					"circle-stroke-width": 1,
					"circle-stroke-color": "rgba(0, 0, 0, .25)"
				}
			});
                        map.setLayoutProperty('codeComplaints', 'visibility', 'none');  // this should not be neccessary and is dirty...
			map.addLayer({
				"id": "allProperties",
				"type": "circle",
				"source": "propertyData",
				"source-layer": "props_all_10_1-8amcho",//"outputmap-dss2ey",   //change this from map_box
                                "metadata": {
                                 "mapbox:filter-1": "False",
                                 "mapbox:filter-3": "False",
                                 "mapbox:filter-10": "False",
                                 "mapbox:filter-100": "False"
                                },
                        	"paint": {
					"circle-radius": defaultRadius,
					"circle-color": defaultColors,
					"circle-opacity": defaultOpacity,
					"circle-stroke-width": 1,
					"circle-stroke-color": "rgba(0, 0, 0, .25)"
				}
			});

			// Disable functionality if IE
			if (checkIE() == true) {
				// Show unsupported message
				searchInput.value = "Internet Explorer isn't supported. Try Chrome!";
				searchInput.disabled = true;
				searchInputContainer.style.display = "block";
			} else {
				// Remove persisted value
				searchInput.value = "";
				// Show search
				searchInputContainer.style.display = "block";
				// Add input listeners
				searchInput.addEventListener("keypress", matchAddresses);
				searchInput.addEventListener("input", matchAddresses); // Registers backspace
				// Allow hover and click
				setHoverState("propertyData", "features", "allProperties");
			};

			// Hide spinner
			spinner.style.display = "none";
		};
	};
	request.send();
});

map.on("error", function(e) {
	// Don't log empty tile errors
	if (e && e.error.status != 403) {
		console.error(e);
	};
});

function addLayer (name, data, radius, color, opacity) {
	// Set source data
	map.addSource(name, {
		type: "geojson",
		data: data,
		promoteId: propertyIndexColumn
	});

	// Add to map
	map.addLayer({
		"id": name,
		"type": "circle",
		"source": name,
		"paint": {
			"circle-radius": radius,
			"circle-color": color,
			"circle-opacity": opacity,
			"circle-stroke-width": 2,
			"circle-stroke-color": "rgba(0, 0, 0, .25)",
		},
	});

	// Style hover
	setHoverState(data, null, name);
};

function setHoverState (sourceData, sourceLayer, hoverLayer) {
	// Building under cursor
	var buildingAtPoint = null;
	// Declared here to fix duplicates
	var buildingID = null;

	map.on("mousemove", hoverLayer, function(e) {
		var featuresAtPoint = map.queryRenderedFeatures(e.point, { layers: [hoverLayer] });
		if (sourceLayer != null) {
			// Vector source
			buildingAtPoint = getBuildingAtPoint(featuresAtPoint, sourceData);
		} else {
			// GeoJSON source
			buildingAtPoint = getBuildingAtPoint(featuresAtPoint, hoverLayer);
		};

		if (buildingAtPoint) {
			map.getCanvas().style.cursor = "pointer";
			// Remove existing state
			if (buildingID) {
				if (sourceLayer != null) {
					// Vector source
					map.removeFeatureState({
						source: sourceData,
						sourceLayer: sourceLayer
					});
				} else {
					// GeoJSON source
					map.removeFeatureState({
						source: hoverLayer,
						id: buildingID
					});
				};
			};
			
			// Set new ID
			buildingID = featuresAtPoint[0].properties[propertyIndexColumn];

			// Hover to true
			if (sourceLayer != null) {
				// Vector source
				map.setFeatureState({
					source: sourceData,
					sourceLayer: sourceLayer,
					id: buildingID
				}, {
					hover: true
				});
			} else {
				// GeoJSON source
				map.setFeatureState({
					source: hoverLayer,
					id: buildingID
				}, {
					hover: true
				});
			};
		} else {
			// Clear var
			buildingAtPoint = null;
		};
	});

	map.on("click", hoverLayer, function(e) {
		// Hover to false
		if (buildingID) {
			if (sourceLayer != null) {
				// Vector source
				map.setFeatureState({
					source: sourceData,
					sourceLayer: sourceLayer,
					id: buildingID
				}, {
					hover: false
				});
			} else {
				// GeoJSON source
				map.setFeatureState({
					source: hoverLayer,
					id: buildingID
				}, {
					hover: false
				});
			};	
		};

		// Select property
		if (buildingAtPoint) {
			// Reset UI
			resetMap();
			// Update it
			renderSelectedUI(buildingAtPoint);
			// Log event
			firebase.analytics().logEvent("map-point-clicked", { 
				property_address: buildingAtPoint.properties[propertyAddressColumn],
				taxpayer: buildingAtPoint.properties[taxpayerColumn],
				affiliated_with: buildingAtPoint.properties[affiliatedWithColumn],
			});
		};
	});

	map.on("mouseleave", hoverLayer, function() {
		// Hover to false
		if (buildingID) {
			if (sourceLayer != null) {
				// Vector source
				map.setFeatureState({
					source: sourceData,
					sourceLayer: sourceLayer,
					id: buildingID
				}, {
					hover: false
				});
			} else {
				// GeoJSON source
				map.setFeatureState({
					source: hoverLayer,
					id: buildingID
				}, {
					hover: false
				});
			};	
		};
		
		// Clear var
		buildingID = null;
		
		// Restore cursor
		map.getCanvas().style.cursor = "";
	});
};

function getBuildingAtPoint (features, source) {
	var filtered = features.filter(function(feature) {
		var pointSource = feature.layer.source;
		// Return feature when trimmed input is found in buildings array
		return pointSource.indexOf(source) > -1;
	});
	return filtered[0];
};
