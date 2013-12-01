//BUG FIX BY AlejandroNova (AN)

layout = new LinearLayout(plasmoid);

$ = {};

layout.alignment = QtAlignHCenter
layout.setContentsMargins(5,5,10,5)
//AN: I don't think an aspect ratio is useful here.
plasmoid.aspectRatioMode = IgnoreAspectRatio;

label= new Label();
layout.addItem(label);

var status=false;
var startdate= new Date(0,0,0,0,0,0);
//AN: I changed the font to Lato, because I love it. Please, don't hardcode the font!
var mfont = new QFont("Lato", 30);


drawButtons();
playb.clicked.connect(toggleLabel);

//AN: Added mhours to keep track of hours. Sometimes I need a 24 hour stopwatch.
var mseconds = 0, mminutes = 0, mhours = 0;




plasmoid.dataUpdated= function(name, data) {
		
		if( status ){
		mseconds = startdate.getUTCSeconds()+1;
		} else {
		mseconds = startdate.getUTCSeconds();
		}
		startdate.setUTCSeconds(mseconds);
		if (mseconds <= 9) 
			mseconds = "0"+ mseconds;
		mminutes = startdate.getUTCMinutes();
		startdate.setUTCMinutes(mminutes);
		if( mminutes <= 9)
			mminutes="0"+mminutes;
			
		mhours = startdate.getUTCHours();
		if( mhours <= 9)
			mhours="0" + mhours;

		label.font = mfont;
		//AN: Now we display mhours:mminutes:mseconds
		label.text = mhours + ":" + mminutes + ":"+ mseconds;
		
}

dataEngine("time").connectSource("Local",plasmoid,1000);

function drawButtons(){
	playb = new PushButton();
	playb.text="Start";
	layout.addItem(playb);
}

function toggleLabel( ){
	if(playb.text == "Start"){
		playb.text="Stop";
		status=true;
		
	} else if ( playb.text == "Stop") {
		playb.text = "Start";
		status=false;
	}
}


/*AN: This is the bugfix. You need to reset Date just like you did it before.
Three zeros are enough, one is not*/
//PC: thanks :)

plasmoid.action_ResetTime = function() { startdate = new Date(0,0,0);  print(startdate); };

//AN: FIXME: We need a better way to take care of this timer!
//PC: any ideias?
plasmoid.setAction("ResetTime", i18n("Reset Time"), "chronometer")



