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

//This array will store the modelIds in order
var meshIDArray=[];

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

           
           // scene.loadFromViewURL("models/"+"flipped"); 
         /*
            scene.loadFromViewURL("models/"+patientID+"_surface"); //id will be 1000 + 1
            scene.loadFromViewURL("models/"+patientID+"_bile"); // //id will be 1000 + 2
            scene.loadFromViewURL("models/"+patientID+"_hepatic_vein");//id will be 1000 + 3
            scene.loadFromViewURL("models/"+patientID+"_portal");//id will be 1000 + 4
         */
            
            
           /* 
             scene.loadFromViewURL("liverModels/surface"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/bile"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/hepatic"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/portal"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/arterial"+patientID); //id will be 1000 + 1
           */
           scene.loadFromViewURL("liverModels/strahler"+patientID); 
            
            
            
            
        } else {

            scene.resetView();


        }


        zincRenderer.setCurrentScene(scene);
       
        zincRenderer.addToScene(plane);
        
         var current_scene = zincRenderer.getCurrentScene();
        
    }
}

function initialize_scene(){
     // if (currentPatient != patientID) {
        var scene = zincRenderer.getSceneByName("Default")

        if (scene == undefined) {

            scene = zincRenderer.createScene("Default");
        }   else {

            scene.resetView();


        }
    
    zincRenderer.setCurrentScene(scene);
       
        zincRenderer.addToScene(plane);
        
         var current_scene = zincRenderer.getCurrentScene();
}
/*
This function will load strahler groups from 2-8
Assuming there are files strahlerGroup$i_1, where $i = 2...8
and also strahlerGroup$i_view.json
*/
function loadVesselGroup(LIVER_STRING_PRE,NUM_GEOMETRY) {
  
           
           // scene.loadFromViewURL("models/"+"flipped"); 
         /*
            scene.loadFromViewURL("models/"+patientID+"_surface"); //id will be 1000 + 1
            scene.loadFromViewURL("models/"+patientID+"_bile"); // //id will be 1000 + 2
            scene.loadFromViewURL("models/"+patientID+"_hepatic_vein");//id will be 1000 + 3
            scene.loadFromViewURL("models/"+patientID+"_portal");//id will be 1000 + 4
         */
            
            
           /* 
             scene.loadFromViewURL("liverModels/surface"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/bile"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/hepatic"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/portal"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/arterial"+patientID); //id will be 1000 + 1
           */
            
         //  scene.loadFromViewURL("liverModels/strahler15");
            var scene = zincRenderer.getSceneByName("Default")
            for ( var i =2; i <1+ NUM_GEOMETRY; i ++ ) {
                scene.loadFromViewURL("liverModels/"+LIVER_STRING_PRE+i.toString()); 
               // alert(i);
                
            }
           scene.loadFromViewURL("liverModels/"+LIVER_STRING_PRE+"0");
            
            
            
            
       


        
        
  //  }
}


function loadSurfaceGroup(LIVER_STRING_PRE,NUM_GEOMETRY) {


           
           // scene.loadFromViewURL("models/"+"flipped"); 
         /*
            scene.loadFromViewURL("models/"+patientID+"_surface"); //id will be 1000 + 1
            scene.loadFromViewURL("models/"+patientID+"_bile"); // //id will be 1000 + 2
            scene.loadFromViewURL("models/"+patientID+"_hepatic_vein");//id will be 1000 + 3
            scene.loadFromViewURL("models/"+patientID+"_portal");//id will be 1000 + 4
         */
            
            
           /* 
             scene.loadFromViewURL("liverModels/surface"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/bile"+patientID); //id will be 1000 + 1
            scene.loadFromViewURL("liverModels/hepatic"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/portal"+patientID); //id will be 1000 + 1
           scene.loadFromViewURL("liverModels/arterial"+patientID); //id will be 1000 + 1
           */
            
         //  scene.loadFromViewURL("liverModels/strahler15");
            var scene = zincRenderer.getSceneByName("Default")
            for ( var i =1; i <1+ NUM_GEOMETRY; i ++ ) {
                scene.loadFromViewURL("liverModels/"+LIVER_STRING_PRE+i.toString()); 
               // alert(i);
                
            }
           // scene.loadFromViewURL("liverModels/"+LIVER_STRING_PRE+"0");
            
            
            
            
      

        
  //  }
}
