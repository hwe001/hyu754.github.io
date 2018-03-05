//global flags for visibilitiy, they are all visible at start of program
var surfacePreviousVisibility = true;
var hepaticPreviousVisibility = true;
var portalPreviousVisibility = true;
var bilePreviousVisibility = true;
var arterialPreviousVisibility = true;

//Global flags for visibility of different groups
var strahlerPreviousGroup1 = true;
var strahlerPreviousGroup2 = true;
var strahlerPreviousGroup3 = true;
var strahlerPreviousGroup4 = true;
var strahlerPreviousGroup5 = true;
var strahlerPreviousGroup6 = true;
var strahlerPreviousGroup7 = true;
var strahlerPreviousGroup8 = true;
var strahlerPreviousGroup9 = true;

//When the open button is pressed
function openNav() {
    document.getElementById("mySidenav").style.width = "290px";
    document.getElementById("menu_button").style.width = "0%";

}

//Closing the side navigation
function closeNav(){
    document.getElementById("mySidenav").style.width="0px";
    document.getElementById("menu_button").style.width = "150px";
}

/*Functions for strahler groups*/



function strahlerGroup1Visibility(){


    if(strahlerPreviousGroup1==true){
        strahlerPreviousGroup1=false;
    } else{
        strahlerPreviousGroup1=true;
    }

    if(strahlerPreviousGroup1==false){           
        document.getElementById("strahlerGroup1").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("strahlerGroup1").style.backgroundColor =" #4CAF50";
                                       
    }


}
function strahlerGroup2Visibility(){


    if(strahlerPreviousGroup2==true){
        strahlerPreviousGroup2=false;
    } else{
        strahlerPreviousGroup2=true;
    }

    if(strahlerPreviousGroup2==false){           
        document.getElementById("strahlerGroup2").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("strahlerGroup2").style.backgroundColor =" #4CAF50";
                                       
    }


}

function strahlerGroup3Visibility(){
    if(strahlerPreviousGroup3==true){
        strahlerPreviousGroup3 = false;
    } else {
        strahlerPreviousGroup3 = true;
    }
    
   if(strahlerPreviousGroup3==false){           
        document.getElementById("strahlerGroup3").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("strahlerGroup3").style.backgroundColor =" #4CAF50";
                                       
    }
}

function strahlerGroup4Visibility(){
    if(strahlerPreviousGroup4==true){
        strahlerPreviousGroup4 = false;
    } else {
        strahlerPreviousGroup4 = true;
    }
    
    if(strahlerPreviousGroup4==false){
        document.getElementById("strahlerGroup4").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup4").style.backgroundColor = "#4CAF50";
    }
}

function strahlerGroup5Visibility(){
    if(strahlerPreviousGroup5==true){
        strahlerPreviousGroup5 = false;
    } else {
        strahlerPreviousGroup5 = true;
    }
    
    if(strahlerPreviousGroup5 == false){
        document.getElementById("strahlerGroup5").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup5").style.backgroundColor = "#4CAF50";
    }
}


function strahlerGroup6Visibility(){
    if(strahlerPreviousGroup6==true){
        strahlerPreviousGroup6 = false;
    } else {
        strahlerPreviousGroup6 = true;
    }
    
    if(strahlerPreviousGroup6 == false){
        document.getElementById("strahlerGroup6").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup6").style.backgroundColor = "#4CAF50";
    }
}



function strahlerGroup7Visibility(){
    if(strahlerPreviousGroup7==true){
        strahlerPreviousGroup7 = false;
    } else {
        strahlerPreviousGroup7 = true;
    }
    
    if(strahlerPreviousGroup7 == false){
        document.getElementById("strahlerGroup7").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup7").style.backgroundColor = "#4CAF50";
    }
}

function strahlerGroup8Visibility(){
    if(strahlerPreviousGroup8==true){
        strahlerPreviousGroup8 = false;
    } else {
        strahlerPreviousGroup8 = true;
    }
    
    if(strahlerPreviousGroup8 == false){
        document.getElementById("strahlerGroup8").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup8").style.backgroundColor = "#4CAF50";
    }
}

function strahlerGroup9Visibility(){
    if(strahlerPreviousGroup9==true){
        strahlerPreviousGroup9 = false;
    } else {
        strahlerPreviousGroup9 = true;
    }
    
    if(strahlerPreviousGroup9 == false){
        document.getElementById("strahlerGroup9").style.backgroundColor = "darkgreen";
    } else{
        document.getElementById("strahlerGroup9").style.backgroundColor = "#4CAF50";
    }
}





function showAllVisibilityStrahler(){
      if(strahlerPreviousGroup1==false){
       strahlerPreviousGroup1=true;
         document.getElementById("strahlerGroup1").style.backgroundColor =" #4CAF50";
   }
    if(strahlerPreviousGroup2==false){
       strahlerPreviousGroup2=true;
         document.getElementById("strahlerGroup2").style.backgroundColor =" #4CAF50";
   }
    
    if(strahlerPreviousGroup3==false){
       strahlerPreviousGroup3=true;
         document.getElementById("strahlerGroup3").style.backgroundColor =" #4CAF50";
   }
    
    if(strahlerPreviousGroup4==false){
       strahlerPreviousGroup4=true;
         document.getElementById("strahlerGroup4").style.backgroundColor =" #4CAF50";
   }
    if(strahlerPreviousGroup5==false){
       strahlerPreviousGroup5=true;
         document.getElementById("strahlerGroup5").style.backgroundColor =" #4CAF50";
   }
    if(strahlerPreviousGroup6==false){
       strahlerPreviousGroup6=true;
         document.getElementById("strahlerGroup6").style.backgroundColor =" #4CAF50";
   }
    if(strahlerPreviousGroup7==false){
       strahlerPreviousGroup7=true;
         document.getElementById("strahlerGroup7").style.backgroundColor =" #4CAF50";
   }
    if(strahlerPreviousGroup8==false){
       strahlerPreviousGroup8=true;
         document.getElementById("strahlerGroup8").style.backgroundColor =" #4CAF50";
   }
     if(strahlerPreviousGroup9==false){
       strahlerPreviousGroup9=true;
         document.getElementById("strahlerGroup9").style.backgroundColor =" #4CAF50";
   }
   
}






//Function for surface visibility
function surfaceVisibility(){


    if(surfacePreviousVisibility==true){
        surfacePreviousVisibility=false;
    } else{
        surfacePreviousVisibility=true;
    }

    if(surfacePreviousVisibility==false){           
        document.getElementById("surface_button").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("surface_button").style.backgroundColor =" #4CAF50";                                  
    }
}


//Function for surface visibility
function bileVisibility(){


    if(bilePreviousVisibility==true){
        bilePreviousVisibility=false;
    } else{
        bilePreviousVisibility=true;
    }

    if(bilePreviousVisibility==false){           
        document.getElementById("bile_button").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("bile_button").style.backgroundColor =" #4CAF50";
                                       
    }


}


//Function for surface visibility
function portalVisibility(){


    if(portalPreviousVisibility==true){
        portalPreviousVisibility=false;
    } else{
        portalPreviousVisibility=true;
    }

    if(portalPreviousVisibility==false){           
        document.getElementById("portal_button").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("portal_button").style.backgroundColor =" #4CAF50";
                                       
    }


}


//Function for surface visibility
function hepaticVisibility(){


    if(hepaticPreviousVisibility==true){
        hepaticPreviousVisibility=false;
    } else{
        hepaticPreviousVisibility=true;
    }

    if(hepaticPreviousVisibility==false){           
        document.getElementById("hepatic_button").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("hepatic_button").style.backgroundColor =" #4CAF50";
                                       
    }


}


//Function for arterial visibility
function arterialVisibility(){


    if(arterialPreviousVisibility==true){
        arterialPreviousVisibility=false;
    } else{
        arterialPreviousVisibility=true;
    }

    if(arterialPreviousVisibility==false){           
        document.getElementById("arterial_button").style.backgroundColor ="darkgreen";
                                        
    } else{
        document.getElementById("arterial_button").style.backgroundColor =" #4CAF50";
                                       
    }


}


//Function to show all geometries
function allVisibility(){


   if(surfacePreviousVisibility==false){
       surfacePreviousVisibility=true;
       document.getElementById("surface_button").style.backgroundColor =" #4CAF50";                   
   }
     if(hepaticPreviousVisibility==false){
       hepaticPreviousVisibility=true;
         document.getElementById("hepatic_button").style.backgroundColor =" #4CAF50";
   }
     if(portalPreviousVisibility==false){
       portalPreviousVisibility=true;
         document.getElementById("portal_button").style.backgroundColor =" #4CAF50";
   }
     if(bilePreviousVisibility==false){
       bilePreviousVisibility=true;
         document.getElementById("bile_button").style.backgroundColor =" #4CAF50";
         
   }
     if(arterialPreviousVisibility==false){
       arterialPreviousVisibility=true;
         document.getElementById("arterial_button").style.backgroundColor =" #4CAF50";
   }
   


}