/*
Modified Paul's work
By David Yu
*/

//Create a new JSONLoader
var jloader = new THREE.JSONLoader();

//global mesh variable
var meshGlobal;
//Some common materials
var surface_material = new THREE.MeshPhongMaterial({color: "rgb(190,100,90)", opacity: 0.8, transparent: true});


//Create functionss to load goemtry

var loadGeometryThreeJS = function(geometry){

    var meshGlobal = THREE.Mesh(geometry, surface_material);
    meshGlobal.ID = 0;
    meshGlobal.name = "surface";
    zincRenderer.addToScene(meshGlobal);

}


//Load json models to ZINC
//The input will be the patient ID: i.e. S01
//It is assumed that in the foler ./models there exists
// model_name_{bile,portal,hepatic,surface}_{1,view}.JSON 
function loadLiverGroup(patientID) {
    if (currentPatient != patientID) {
        var scene = zincRenderer.getSceneByName(patientID)

        if (scene == undefined) {

            scene = zincRenderer.createScene(patientID);

            scene.loadFromViewURL("models/"+patientID+"_surface"); //id will be 1000 + 1
            scene.loadFromViewURL("models/"+patientID+"_bile"); // //id will be 1000 + 2
            scene.loadFromViewURL("models/"+patientID+"_hepatic_vein");//id will be 1000 + 3
            scene.loadFromViewURL("models/"+patientID+"_portal");//id will be 1000 + 4
            
        } else {

            scene.resetView();


        }


        zincRenderer.setCurrentScene(scene);
       
        zincRenderer.addToScene(plane);
        
         var current_scene = zincRenderer.getCurrentScene();
        
    }
}

