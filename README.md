# Find My Landlord ATX
This project was completed by Chris Correll using the Chicago DSA chapters find my land lord tool as a basis for the web visualization. You can find their source code [here](https://github.com/ChicagoDSA/find-my-landlord).

The data set was compiled and extracted from data from [Travis County Appraisal District](https://www.traviscad.org/reports-request/), [Travis County Land Use Inventory](https://data.austintexas.gov/Locations-and-Maps/Land-Use-Inventory-Detailed/fj9m-h5qy), [Building and developement data from the City of Austin](https://data.austintexas.gov/Building-and-Development/Land-Database-2016/nuca-fzpt), and [the US Census](https://geocoding.geo.census.gov/). 

The information is made available as a public service. However, the owner makes no warranty as to the accuracy, reliability, or completeness of the information and is not responsible for any errors or omissions or for results obtained from the use of the information. Distribution of the information does not constitute such a warranty. Use of the information is the sole responsibility of the user.

The web app allows tenants to:
- Look up any registered rental property in Travis County
- View the rental's owner, browse related properties, and download these as a PDF

Check it out [here](https://funkonaut.github.io/find-my-landlord-atx).

## Credits
[Mapbox](https://www.mapbox.com/) powers the map's tileset and hosts the map, [Google Cloud Firestore](https://firebase.google.com/docs/firestore) hosts our database, and [jsPDF](https://github.com/MrRio/jsPDF) generates PDFs.
