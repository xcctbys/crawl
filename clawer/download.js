// download page
// Usage:
//     phantomjs download.js url [cookie]


var system = require('system');
var page = require('webpage').create();
var url = system.args[1];
var cookie = "";

if(system.args.length > 1) {
	cookie = system.args[2];
}

page.settings.resourceTimeout = 30*1000; 
page.settings.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0';
page.settings.localToRemoteUrlAccessEnabled = true;
page.settings.loadImages = false;
page.settings.javascriptEnabled = true;


page.onResourceTimeout = function(e) {
  console.error(e.errorCode);   // it'll probably be 408 
  console.error(e.errorString); // it'll probably be 'Network timeout on resource'
  phantom.exit(1);
};



// jQuery is loaded, now manipulate the DOM
page.open(url, function(status) {

	if(status != "success") {
		console.error("status ", status);
		phantom.exit(1);
		return;
	}
	
	var sc = page.evaluate(function(){
		return document.body.innerHTML;
	});
	
	window.setTimeout(function(){
		page.render('download.png');
		console.log(sc);
		phantom.exit();	
	});
	
	
});
	



