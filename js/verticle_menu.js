//global flags for visibilitiy, they are all visible at start of program
var surfacePreviousVisibility=true;
var hepaticPreviousVisibility=true;
var portalPreviousVisibility=true;
var bilePreviousVisibility=true;
var arterialPreviousVisibility=true;

//When the open button is pressed
function openNav(){
    document.getElementById("mySidenav").style.width = "290px";
    document.getElementById("menu_button").style.width = "0%";

}

//Closing the side navigation
function closeNav(){
    document.getElementById("mySidenav").style.width="0px";
    document.getElementById("menu_button").style.width = "150px";
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
   }
     if(hepaticPreviousVisibility==false){
       hepaticPreviousVisibility=true;
   }
     if(portalPreviousVisibility==false){
       portalPreviousVisibility=true;
   }
     if(bilePreviousVisibility==false){
       bilePreviousVisibility=true;
   }
     if(arterialPreviousVisibility==false){
       arterialPreviousVisibility=true;
   }
   


}