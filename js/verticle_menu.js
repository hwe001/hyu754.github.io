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