// Initialize Cloud Firestore through Firebase
  // Your web app's Firebase configuration
  var firebaseConfig = {
    apiKey: "AIzaSyBABV3FPVBoSK2dMEZS7YHJxJyG_rc1dSg",
    authDomain: "find-my-landlord-atx.firebaseapp.com",
    databaseURL: "https://find-my-landlord-atx.firebaseio.com",
    projectId: "find-my-landlord-atx",
    storageBucket: "find-my-landlord-atx.appspot.com",
    messagingSenderId: "445881229179",
    appId: "1:445881229179:web:9943a876434e09635e67de",
    measurementId: "G-WR3K8FC8CB"
  };
firebase.initializeApp(firebaseConfig);
firebase.analytics();

firebase.auth().signInAnonymously().catch(function(error) {
        console.log(error.code);
        console.log(error.message);
});

var db = firebase.firestore();
var featuresRef = db.collection(databaseCollectionName);

