// Column headers
var propertyAddressColumn = "Property Address";
var communityAreaColumn = "Community Area";
var propertyIndexColumn = "Property Index Number";  //has to be a string?:
var taxpayerColumn = "Taxpayer";
var taxpayerMatchCodeColumn = "Taxpayer Match Code";
var affiliatedWithColumn = "Affiliated With";
var additionalDetailsColumn = "Additional Details";
var ownedColumn = "Properties Held by Taxpayer Match Code";
var unitColumn = "Unit Count from Department of Buildings";
var relativeSizeColumn = unitColumn;//"Relative Size";


// Access token 
mapboxgl.accessToken = 'pk.eyJ1IjoiY3Jjb3JyZWxsIiwiYSI6ImNrZG1ranc4dDE5ODUycGxqeGNnYTIzcGsifQ.scBxw_xzNgfp0Uc7rv56vQ';//'pk.eyJ1IjoiY3Jjb3JyZWxsIiwiYSI6ImNrZG1ranc4dDE5ODUycGxqeGNnYTIzcGsifQ.scBxw_xzNgfp0Uc7rv56vQ';
// Database reference
var databaseCollectionName = "features";
// JSON search
var searchIndex = "https://funkonaut.github.io/find-my-landlord-atx/search_index.json?raw=true";//"https://find-my-landlord.nyc3.cdn.digitaloceanspaces.com/search-index.json";
//var searchIndex ="https://funkonaut.github.io/find-my-landlord-atx/output3.json?raw=true"
// Map tiles
//var tiles = "https://funkonaut.github.io/find-my-landlord-atx/out.mbtiles";
//var tiles ="https://funkonaut.github.io/features/{z}/{x}/{y}.pbf"
//var tiles = "./features/{z}/{x}/{y}.pbf";

// Colors
var dsaRed = "#ec1f27";
var dsaYellow = "#fad434";
var color4 = dsaRed;
var color3 = "#dc7270";
var color2 = "#866b85";
var color1 = "#1e1231";
var black = "#000";
var white = "#fff";
var gray = "#808080";

// Map defaults
var defaultOpacity = .5;
var highlightZoom = 14;

// Change colors based on landlord size
var defaultColors = [
	"case",
	[">=", ["get", ownedColumn], 100],
	color4,
	[">=", ["get", ownedColumn], 10],
	color3,
	[">=", ["get", ownedColumn], 3],
	color2,
	[">", ["get", ownedColumn], 0],
	color1,
	white
];

// Scale radius based on zoom, relative unit size, hover
var defaultRadius = [
	"interpolate",
	["exponential", 1.75],
	["zoom"],
	8, 
	["case",
		["boolean", ["feature-state", "hover"], false],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 10, 100, 20],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 2, 100, 10]
	],
	16, 
	["case",
		["boolean", ["feature-state", "hover"], false],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 12, 100, 24],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 4, 100, 20]
	],
	22, ["case",
		["boolean", ["feature-state", "hover"], false],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 200, 100, 400],
		["interpolate", ["linear"], ["get", relativeSizeColumn], 0, 180, 100, 900]
	]
];

// Custom UI
var selectedBounds = null;
var markerContainer = null;
var marker = null;
var spinner = document.getElementById("spinner");
var searchInputContainer = document.getElementById("search-input-container");
var searchInput = document.getElementById("search-input");
var clearButton = document.getElementById("clear");
var searchResultsContainer = document.getElementById("search-results-container");
var searchResultsCounter = document.getElementById("search-results-counter");
var searchResultsList = document.getElementById("search-results-list");
var selectedContainer = document.getElementById("selected-container");
