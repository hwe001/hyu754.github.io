/*code obtained from : https://github.com/stemkoski/stemkoski.github.com/blob/master/Three.js/Infobox.html*/
$(function() 
{
	 $("#infoBox")
	.css( 
	{
	   "background":"rgba(215,255,255,0.9)"
	})
	.dialog({ autoOpen: false, 
		show: { effect: 'fade', duration: 500 },
		hide: { effect: 'fade', duration: 500 } 
	});
	
	 $("#infoButton")
       .text("Show Surgical Information ") // sets text to empty
	
    
    .button()
	.click( 
		function() 
		{ 
			$("#infoBox").dialog("open");
		});
});