/*var gui = new dat.GUI({
                height : 5*32 - 1
            })*/
var FizzyText = function() {
this.message = 'dat.gui';
this.speed = 0.8;
this.displayOutline = false;
this.showPortal = false;
this.planeSize = 1;
this.explode = function() {};
// Define render logic ...
};

var segmentText_ = function() {
this.seg1 = true;
this.seg2 = true;
this.seg3 = true;
this.seg4 = true;
this.seg5 = true;
this.seg6 = true;
this.seg7 = true;
this.seg8 = true;
this.alpha = 0.7;
// Define render logic ...
};


var hepaticText_ = function() {
this.hep1 = true;
this.hep2 = true;
this.hep3 = true;
this.hep4 = true;
this.hep5 = true;
this.hep6 = true;
this.hep7 = true;
this.hep8 = true;

// Define render logic ...
};
//Add some elements to dat.gui
var params = {
    integration:  1000
}
var text = new FizzyText();
var segmentText  = new segmentText_();
var hepaticText = new hepaticText_();
var gui = new dat.GUI();

//Create different folders
var segmentFolder = gui.addFolder('Liver Segments');
/*segmentFolder.add(segmentText,'seg1')
segmentFolder.add(segmentText,'seg2')
segmentFolder.add(segmentText,'seg3')
segmentFolder.add(segmentText,'seg4')
segmentFolder.add(segmentText,'seg5')
segmentFolder.add(segmentText,'seg6')
segmentFolder.add(segmentText,'seg7')
segmentFolder.add(segmentText,'seg8')*/
segmentFolder.add(segmentText, 'alpha', 0.0, 1.0);



var portalFolder = gui.addFolder('Portal Vein');


var hepaticFolder = gui.addFolder('Hepatic Vein');
portalFolder.add(hepaticText,'hep1')
portalFolder.add(hepaticText,'hep2')
portalFolder.add(hepaticText,'hep3')
portalFolder.add(hepaticText,'hep4')
portalFolder.add(hepaticText,'hep5')
portalFolder.add(hepaticText,'hep6')
portalFolder.add(hepaticText,'hep7')
portalFolder.add(hepaticText,'hep8')

var cameraFolder = gui.addFolder('Camera settings')

cameraFolder.add(text, 'planeSize', -1000, 1000);