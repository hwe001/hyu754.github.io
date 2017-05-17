//This variables will be global variable 
var global_width=undefined;
var global_height=undefined;


//Orientation of the device, if is undefined; we assume a pc here
//Else it will be:
//      verticle:0 or 180
//      horizontal:90 or -90
var previousOrientation = window.orientation;



//Video initialization etc
var video = document.createElement('video');
video.autoplay=true;



var videoTexture = new THREE.Texture(video);
var surface_material_video = new THREE.MeshBasicMaterial ({
    map : videoTexture
});

var videoSelect = document.querySelector('select#videoSource');
var selectors=[videoSelect];
//Gets devices
function gotDevices(deviceInfos) {
    var values = selectors.map(function(select) {
        return select.value;
    });
    selectors.forEach(function(select) {
        while (select.firstChild) {
            select.removeChild(select.firstChild);
        }
    });
    for (var i = 0; i !== deviceInfos.length; ++i) {
        var deviceInfo = deviceInfos[i];
        var option = document.createElement('option');
        
        option.value = deviceInfo.deviceId;

        if (deviceInfo.kind === 'videoinput') {
            option.text = deviceInfo.label || 'camera ' + (videoSelect.length + 1);
            // alert( option.text);
            videoSelect.appendChild(option);
        } else {
            console.log('Some other kind of source/device: ', deviceInfo);
        }
    }
    selectors.forEach(function(select, selectorIndex) {
        if (Array.prototype.slice.call(select.childNodes).some(function(n) {
            return n.value === values[selectorIndex];
        })) {
            select.value = values[selectorIndex];
        }
    });
}

//enumerates the devices
navigator.mediaDevices.enumerateDevices().then(gotDevices).catch(handleError);


//If stream is received
function gotStream(stream) {
    window.stream = stream; // make stream available to console
    video.srcObject = stream;
    // Refresh button list in case labels have become available
    return navigator.mediaDevices.enumerateDevices();
}

function handleError(error) {
    console.log('navigator.getUserMedia error: ', error);
}

//switch value for videoSelect

function start() {
    if (window.stream) {
        window.stream.getTracks().forEach(function(track) {
            track.stop();
        });
    }


    //var audioSource = audioInputSelect.value;
    var videoSource = videoSelect.value;
    
    var constraints = {
        // audio: {deviceId: audioSource ? {exact: audioSource} : undefined},
        video: {deviceId: videoSource ? {exact: videoSource} : undefined}
    };

    //alert(constraints.video);
    navigator.mediaDevices.getUserMedia(constraints).
    then(gotStream).then(gotDevices).catch(handleError);
    //video.addEventListener("loadedmetadata");

    //if the meta data has changed;
    video.onloadedmetadata=function(){
        global_width=this.videoWidth;
        global_height=this.videoHeight;
    
    }
  
    /*
    video.onloadedmetadata = function() {
        console.log('width is', this.videoWidth);
        console.log('height is', this.videoHeight);

        if(this.videoWidth < 10){
            video.width = 480;
        } else {
            video.width = this.videoWidth;
        }

        if(this.videoHeigth <10){
            video.height = 640;
        } else{
            video.height = this.videoHeight;
        }
        // video.width = 480;
        // video.height = 640;

        //alert("f");
        //if it is undefined then it is on a pc (probably)
        if(previousOrientation ==false){
            plane.scale.set(video.width,video.height,1);
        } else{
            plane.scale.set(video.height,video.width,1);
            //if the orientation is verticle
            if ((previousOrientation==0)||(previousOrientation==180)){
                plane.scale.set(video.height,video.width,1);
            } else if((previousOrientation==90)||(previousOrientation==-90)){ 
                //if the device is orizontal
                plane.scale.set(video.width,video.height,1);
            }
        }


        //  alert("width : "+video.width);
        //alert("height : "+video.height);

        //alert("video width is: " +video.width);
        //alert("video height is: "+video.height);
    }
    */
    //alert("video width is: " +video.width);
    //  alert("video height is: "+video.height);
    //video.onloadedmetadata();
    //video.width =1000; 
    //video.Height =1000; 
    console.log(video.width);
    console.log(video.height);
}

videoSelect.onchange = start;
//checkOrientation();
start();

//Function for resizing the image plane in Zinc if the orientation is changed
var checkOrientation = function(){
    if(previousOrientation!==undefined){
        if(window.orientation!==previousOrientation){

            previousOrientation = window.orientation;
            
            //If the current orientation is horizontal we switch width <-> height 
            var dummyGlobalHeight = global_height;
            global_height = global_width;
            global_width = dummyGlobalHeight;
          //  alert(previousOrientation);
            if((previousOrientation==90)||(previousOrientation==-90)){
                document.getElementById('plane-slider').value = 400;
                //alert('changed');
            } else if((previousOrientation==0)||(previousOrientation==180)){
                 document.getElementById('plane-slider').value = 0;
            }
        }
    }
}

 window.addEventListener("orientationchange", checkOrientation, false);




